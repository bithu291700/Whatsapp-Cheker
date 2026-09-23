// WhatsApp Checker Bot - Railway Pairing Fix
// Based on the user's original bot. Pairing flow updated for current Baileys behavior.

const crypto = require('crypto');
if (!global.crypto) {
    global.crypto = crypto;
}

const baileys = require('@whiskeysockets/baileys');
const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    Browsers,
    makeCacheableSignalKeyStore
} = baileys;

const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const fs = require('fs');
const path = require('path');
const pino = require('pino');
const QRCode = require('qrcode');

const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
const ADMIN_ID = 7388500439;
const currentPassword = "291736";

if (!TELEGRAM_TOKEN) {
    console.error("CRITICAL ERROR: TELEGRAM_TOKEN missing!");
    process.exit(1);
}

// Railway web server
const app = express();
const PORT = process.env.PORT || 8080;

app.get('/', (req, res) => {
    res.status(200).send('WhatsApp Bot Active!');
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server listening on port ${PORT}`);
});

const bot = new TelegramBot(TELEGRAM_TOKEN, { polling: true });

bot.on('polling_error', (err) => {
    console.error("Telegram polling error:", err?.message || err);
});

process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (reason) => {
    console.error('Unhandled Rejection:', reason);
});

const userSockets = {};
const userStates = {};
const authenticatedUsers = new Set();
const connectionNotified = {};
const pairingInProgress = {};
const pairingModes = {};
const reconnectTimers = {};

function getMainReplyKeyboard() {
    return {
        keyboard: [
            [{ text: "🔢 Pair via Code" }],
            [{ text: "📷 Pair via QR" }],
            [{ text: "📱 Check Number" }, { text: "ℹ️ Help & Status" }]
        ],
        resize_keyboard: true
    };
}

function ensureDirExists(dirPath) {
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
}

function cleanPhoneNumber(value) {
    return String(value || '').replace(/\D/g, '');
}

function isValidInternationalNumber(phone) {
    // WhatsApp pairing requires country code and digits only.
    return /^\d{8,15}$/.test(phone);
}

function getStatusCode(lastDisconnect) {
    return lastDisconnect?.error?.output?.statusCode ??
        lastDisconnect?.error?.statusCode ??
        lastDisconnect?.error?.data?.statusCode;
}

async function getLatestVersionIfAvailable() {
    // Newer Baileys versions export this helper. Older versions may not,
    // so the bot remains compatible with installations that don't export it.
    try {
        if (typeof baileys.fetchLatestBaileysVersion === 'function') {
            const result = await baileys.fetchLatestBaileysVersion();
            if (result?.version) {
                console.log(
                    `WhatsApp Web version: ${result.version.join('.')} | latest=${result.isLatest}`
                );
                return result.version;
            }
        }
    } catch (err) {
        console.error("Could not fetch latest WhatsApp Web version:", err?.message || err);
    }
    return undefined;
}

async function destroySocket(chatId, removeSession = false) {
    const socket = userSockets[chatId];

    if (socket) {
        try {
            socket.ev.removeAllListeners('connection.update');
        } catch (e) {}

        try {
            socket.end(undefined);
        } catch (e) {}

        delete userSockets[chatId];
    }

    if (removeSession) {
        const sessionDir = path.join(__dirname, 'sessions', `session_${chatId}`);
        if (fs.existsSync(sessionDir)) {
            try {
                fs.rmSync(sessionDir, { recursive: true, force: true });
            } catch (e) {
                console.error("Session cleanup error:", e?.message || e);
            }
        }
    }
}

async function createWhatsAppConnection(chatId, phoneToPair = null, mode = 'pairing', isReconnect = false) {
    const baseDir = path.join(__dirname, 'sessions');
    ensureDirExists(baseDir);

    const sessionDir = path.join(baseDir, `session_${chatId}`);

    // A brand-new pairing starts with a clean session. Reconnects NEVER delete it.
    if (phoneToPair && !isReconnect) {
        await destroySocket(chatId, true);
    } else if (userSockets[chatId]) {
        await destroySocket(chatId, false);
    }

    ensureDirExists(sessionDir);

    const { state, saveCreds } = await useMultiFileAuthState(sessionDir);
    const latestVersion = await getLatestVersionIfAvailable();

    const socketConfig = {
        logger: pino({ level: 'warn' }),
        browser: mode === 'qr'
            ? Browsers.ubuntu('Chrome')
            : Browsers.windows('Chrome'),
        printQRInTerminal: false,
        auth: {
            creds: state.creds,
            keys: makeCacheableSignalKeyStore(
                state.keys,
                pino({ level: 'silent' })
            )
        },
        markOnlineOnConnect: false,
        generateHighQualityLinkPreview: false,
        syncFullHistory: false,
        connectTimeoutMs: 60_000,
        keepAliveIntervalMs: 25_000,
        retryRequestOnRetry: true
    };

    if (latestVersion) socketConfig.version = latestVersion;

    const waSock = makeWASocket(socketConfig);
    userSockets[chatId] = waSock;
    waSock.ev.on('creds.update', saveCreds);

    let authMessageSent = false;
    let codeRequested = false;

    const requestCode = async () => {
        if (mode !== 'pairing' || !phoneToPair || codeRequested || state.creds.registered) return;

        const cleanPhone = cleanPhoneNumber(phoneToPair);
        if (!isValidInternationalNumber(cleanPhone)) {
            throw new Error("Invalid phone number. Use country code + digits only.");
        }

        codeRequested = true;
        try {
            console.log(`Requesting pairing code for ${cleanPhone}`);
            const rawCode = await waSock.requestPairingCode(cleanPhone);

            if (!rawCode) throw new Error("WhatsApp returned an empty pairing code.");

            const code = rawCode.match(/.{1,4}/g)?.join("-") || rawCode;

            await bot.sendMessage(
                chatId,
                `🔑 **Pairing Code:** \`${code}\`\n\n` +
                `WhatsApp → Linked Devices → Link with phone number instead → code দিন।\n\n` +
                `⚠️ Code দেওয়ার পর কয়েক সেকেন্ড অপেক্ষা করুন। 515 এলে bot automatic reconnect করবে।`,
                {
                    parse_mode: "Markdown",
                    reply_markup: {
                        inline_keyboard: [[
                            { text: "❌ Cancel Pairing", callback_data: "cancel_pairing" }
                        ]]
                    }
                }
            );

            authMessageSent = true;
            console.log(`Pairing code sent to Telegram chat ${chatId}`);
        } catch (err) {
            codeRequested = false;
            console.error("Pairing Request Error:", err);

            await bot.sendMessage(
                chatId,
                `❌ Pairing code তৈরি করা যায়নি.\n\nError: ${err?.message || 'Unknown error'}`,
                { reply_markup: getMainReplyKeyboard() }
            );

            pairingInProgress[chatId] = false;
        }
    };

    const sendQr = async (qr) => {
        if (mode !== 'qr' || !qr) return;

        try {
            const image = await QRCode.toBuffer(qr, {
                type: 'png',
                width: 420,
                margin: 2,
                errorCorrectionLevel: 'M'
            });

            await bot.sendPhoto(
                chatId,
                image,
                {
                    caption:
                        "📷 **WhatsApp QR Code**\n\n" +
                        "WhatsApp → Linked Devices → Link a device → এই QR scan করুন।\n\n" +
                        "⚠️ QR-এর মেয়াদ শেষ হলে নতুন QR automatically পাঠানো হবে।",
                    parse_mode: "Markdown"
                }
            );

            authMessageSent = true;
            console.log(`QR code sent to Telegram chat ${chatId}`);
        } catch (err) {
            console.error("QR send error:", err);
            await bot.sendMessage(
                chatId,
                `❌ QR পাঠানো যায়নি.\n\nError: ${err?.message || 'Unknown error'}`,
                { reply_markup: getMainReplyKeyboard() }
            );
            pairingInProgress[chatId] = false;
        }
    };

    waSock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;
        const statusCode = Number(getStatusCode(lastDisconnect) || 0);

        console.log(
            `WA connection update [${chatId}]: connection=${connection || '-'} ` +
            `status=${statusCode || '-'} qr=${!!qr} mode=${mode}`
        );

        // QR mode: send every fresh QR to Telegram.
        if (mode === 'qr' && qr) {
            await sendQr(qr);
        }

        // Pairing-code mode: Baileys exposes the initial QR-stage event before
        // requestPairingCode is safe on the normal flow.
        if (
            mode === 'pairing' &&
            phoneToPair &&
            !codeRequested &&
            !state.creds.registered &&
            qr
        ) {
            await requestCode();
        }

        // Some versions may not emit QR before the pairing request. Fallback once.
        if (
            mode === 'pairing' &&
            phoneToPair &&
            !codeRequested &&
            !state.creds.registered &&
            connection === 'connecting'
        ) {
            setTimeout(() => {
                requestCode().catch(err =>
                    console.error("Pairing fallback error:", err)
                );
            }, 1800);
        }

        if (connection === 'open') {
            pairingInProgress[chatId] = false;
            connectionNotified[chatId] = true;
            authMessageSent = true;

            await bot.sendMessage(
                chatId,
                "🎉 **WhatsApp Connected Successfully!**\n\n" +
                "এখন **📱 Check Number** option ব্যবহার করতে পারেন।",
                {
                    parse_mode: "Markdown",
                    reply_markup: getMainReplyKeyboard()
                }
            );

            return;
        }

        if (connection === 'close') {
            connectionNotified[chatId] = false;
            delete userSockets[chatId];

            console.error(
                `WhatsApp connection closed [${chatId}], status=${statusCode || 'unknown'}`
            );

            // 515 means the server asked the companion connection to restart.
            // Keep the same session; DO NOT delete credentials and DO NOT ask
            // for another code/QR immediately.
            if ([515, 408, 428, 503].includes(statusCode) && !state.creds.registered) {
                if (reconnectTimers[chatId]) return;

                reconnectTimers[chatId] = setTimeout(async () => {
                    delete reconnectTimers[chatId];

                    try {
                        console.log(`Restarting WhatsApp socket after status ${statusCode}...`);
                        await createWhatsAppConnection(
                            chatId,
                            phoneToPair,
                            mode,
                            true
                        );
                    } catch (err) {
                        console.error("Automatic pairing reconnect failed:", err);
                        pairingInProgress[chatId] = false;

                        await bot.sendMessage(
                            chatId,
                            `❌ WhatsApp reconnect failed (code ${statusCode}).\n` +
                            `Pairing/QR session আবার শুরু করতে হবে।`,
                            { reply_markup: getMainReplyKeyboard() }
                        );
                    }
                }, 2000);

                return;
            }

            // After the account is registered, normal temporary disconnects can
            // reconnect using the saved credentials.
            if (state.creds.registered && statusCode !== DisconnectReason.loggedOut) {
                if (reconnectTimers[chatId]) return;

                reconnectTimers[chatId] = setTimeout(async () => {
                    delete reconnectTimers[chatId];

                    try {
                        await createWhatsAppConnection(
                            chatId,
                            null,
                            pairingModes[chatId] || mode,
                            true
                        );
                    } catch (err) {
                        console.error("Registered-session reconnect failed:", err);
                    }
                }, 2500);

                return;
            }

            if (statusCode === DisconnectReason.loggedOut) {
                try {
                    fs.rmSync(sessionDir, { recursive: true, force: true });
                } catch (e) {}

                pairingInProgress[chatId] = false;
                delete pairingModes[chatId];

                await bot.sendMessage(
                    chatId,
                    "⚠️ WhatsApp session logged out. আবার Pair via Code অথবা Pair via QR করুন।",
                    { reply_markup: getMainReplyKeyboard() }
                );
            }
        }
    });

    // Initial fallback for QR mode if an update arrives without QR immediately.
    if (mode === 'pairing' && phoneToPair && !state.creds.registered) {
        setTimeout(() => {
            requestCode().catch(err =>
                console.error("Initial pairing fallback error:", err)
            );
        }, 3500);
    }

    return waSock;
}

bot.on('callback_query', async (query) => {
    const chatId = query.message.chat.id;
    const data = query.data;

    if (data === "cancel_pairing") {
        delete userStates[chatId];
        pairingInProgress[chatId] = false;
        delete pairingModes[chatId];
        if (reconnectTimers[chatId]) {
            clearTimeout(reconnectTimers[chatId]);
            delete reconnectTimers[chatId];
        }

        await destroySocket(chatId, true);

        await bot.answerCallbackQuery(query.id, {
            text: "Pairing Cancelled!"
        });

        await bot.editMessageText(
            "🚫 **Pairing attempt cancelled.**",
            {
                chat_id: chatId,
                message_id: query.message.message_id,
                parse_mode: "Markdown"
            }
        );

        await bot.sendMessage(
            chatId,
            "Main menu-te firiye neya holo:",
            { reply_markup: getMainReplyKeyboard() }
        );
    }
});

bot.onText(/\/(start|strat|help)/i, (msg) => {
    const chatId = msg.chat.id;

    if (msg.from.id === ADMIN_ID || authenticatedUsers.has(chatId)) {
        authenticatedUsers.add(chatId);

        bot.sendMessage(
            chatId,
            "👋 **WhatsApp Checker Control Panel:**",
            {
                parse_mode: "Markdown",
                reply_markup: getMainReplyKeyboard()
            }
        );
    } else {
        userStates[chatId] = "WAITING_FOR_PASSWORD";

        bot.sendMessage(
            chatId,
            "🔒 **Password Required!** Password din:"
        );
    }
});

bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text?.trim();

    if (!text || text.startsWith('/')) {
        return;
    }

    if (!authenticatedUsers.has(chatId) && msg.from.id !== ADMIN_ID) {
        if (text === currentPassword) {
            authenticatedUsers.add(chatId);
            delete userStates[chatId];

            return bot.sendMessage(
                chatId,
                "🎉 Access Granted!",
                { reply_markup: getMainReplyKeyboard() }
            );
        }

        return bot.sendMessage(chatId, "❌ Bhul Password!");
    }

    if (text === "🔢 Pair via Code") {
        if (pairingInProgress[chatId]) {
            return bot.sendMessage(
                chatId,
                "⏳ Pairing already cholche. Current attempt cancel kore abar try korun."
            );
        }

        userStates[chatId] = "WAITING_FOR_LINK_NUMBER";

        return bot.sendMessage(
            chatId,
            "📲 WhatsApp Number (Country Code সহ, e.g. `8801700000000`):",
            { parse_mode: "Markdown" }
        );
    }

    if (text === "📷 Pair via QR") {
        if (pairingInProgress[chatId]) {
            return bot.sendMessage(
                chatId,
                "⏳ Pairing already cholche. Current attempt cancel kore abar try korun."
            );
        }

        pairingInProgress[chatId] = true;
        pairingModes[chatId] = 'qr';

        await bot.sendMessage(chatId, "📷 QR connection initialize hocche...");

        try {
            await createWhatsAppConnection(chatId, null, 'qr', false);
        } catch (err) {
            console.error("QR connection creation error:", err);
            pairingInProgress[chatId] = false;

            await bot.sendMessage(
                chatId,
                `❌ QR connection initialize failed.\n\nError: ${err?.message || 'Unknown error'}`,
                { reply_markup: getMainReplyKeyboard() }
            );
        }

        return;
    }

    if (text === "📱 Check Number") {
        const waSock = userSockets[chatId];

        const isConnected = Boolean(
            waSock &&
            (
                waSock.user ||
                waSock.authState?.creds?.me ||
                waSock.authState?.creds?.registered
            )
        );

        if (!isConnected) {
            return bot.sendMessage(
                chatId,
                "⚠️ Prothome **🔢 Pair via Code** koren!",
                { reply_markup: getMainReplyKeyboard() }
            );
        }

        userStates[chatId] = "WAITING_FOR_CHECK_NUMBER";

        return bot.sendMessage(
            chatId,
            "🔍 Number din (e.g. `8801800000000`):",
            { parse_mode: "Markdown" }
        );
    }

    if (text === "ℹ️ Help & Status") {
        const waSock = userSockets[chatId];

        const isConnected = (
            waSock &&
            (
                waSock.user ||
                waSock.authState?.creds?.me ||
                waSock.authState?.creds?.registered
            )
        )
            ? "✅ Connected"
            : "❌ Not Connected";

        return bot.sendMessage(
            chatId,
            `ℹ️ **Status:** ${isConnected}`,
            { reply_markup: getMainReplyKeyboard() }
        );
    }

    const state = userStates[chatId];

    if (state === "WAITING_FOR_LINK_NUMBER") {
        delete userStates[chatId];

        const phone = cleanPhoneNumber(text);

        if (!isValidInternationalNumber(phone)) {
            return bot.sendMessage(
                chatId,
                "❌ Number ভুল। Country code সহ শুধু digits দিন।\nExample: `8801700000000`",
                { parse_mode: "Markdown", reply_markup: getMainReplyKeyboard() }
            );
        }

        pairingInProgress[chatId] = true;
        pairingModes[chatId] = 'pairing';

        await bot.sendMessage(
            chatId,
            "⏳ WebSocket Connection initialize hocche..."
        );

        try {
            await createWhatsAppConnection(chatId, phone);
        } catch (err) {
            console.error("Connection creation error:", err);

            pairingInProgress[chatId] = false;

            await bot.sendMessage(
                chatId,
                `❌ Connection initialize failed.\n\nError: ${err?.message || 'Unknown error'}`,
                { reply_markup: getMainReplyKeyboard() }
            );
        }

    } else if (state === "WAITING_FOR_CHECK_NUMBER") {
        delete userStates[chatId];
        const waSock = userSockets[chatId];
        if (!waSock) return bot.sendMessage(chatId, "⚠️ WhatsApp connect kora nei!", { reply_markup: getMainReplyKeyboard() });

        const numbers = [...new Set(text.split(/[,\s]+/).map(cleanPhoneNumber).filter(Boolean))];
        if (!numbers.length) return bot.sendMessage(chatId, "❌ কোনো valid number পাওয়া যায়নি।", { reply_markup: getMainReplyKeyboard() });
        if (numbers.length > 500) return bot.sendMessage(chatId, "❌ সর্বোচ্চ 500টি number একসাথে check করা যাবে।", { reply_markup: getMainReplyKeyboard() });
        if (numbers.some(n => !isValidInternationalNumber(n))) return bot.sendMessage(chatId, "❌ Number ভুল। Country code সহ শুধু digits দিন।", { reply_markup: getMainReplyKeyboard() });

        await bot.sendMessage(chatId, `⏳ মোট **${numbers.length}**টি number checking শুরু হয়েছে...`, { parse_mode: "Markdown" });
        let batch = [];
        for (const checkPhone of numbers) {
            const jid = `${checkPhone}@s.whatsapp.net`;
            try {
                const [result] = await waSock.onWhatsApp(checkPhone);
                if (!result || !result.exists) {
                    batch.push(`📱 +${checkPhone} — ✅ **FRESH NUMBER**`);
                } else {
                    let profilePic = null, statusBio = null;
                    try { profilePic = await waSock.profilePictureUrl(jid, 'image'); } catch (e) {}
                    try { statusBio = await waSock.fetchStatus(jid); } catch (e) {}
                    const statusText = (!profilePic && !statusBio) ? "⚠️ **SEMI-FRESH (75% Delivery Rate)**" : "❌ **ACTIVE WHATSAPP ACCOUNT**";
                    batch.push(`📱 +${checkPhone} — ${statusText}` + (statusBio?.status ? ` — Bio: ${statusBio.status}` : ""));
                }
            } catch (error) {
                console.error(`Check failed for ${checkPhone}:`, error);
                batch.push(`📱 +${checkPhone} — ❌ **CHECK FAILED**`);
            }
            if (batch.length >= 20) {
                await bot.sendMessage(chatId, batch.join("\n"), { parse_mode: "Markdown" });
                batch = [];
            }
        }
        if (batch.length) await bot.sendMessage(chatId, batch.join("\n"), { parse_mode: "Markdown", reply_markup: getMainReplyKeyboard() });
        else await bot.sendMessage(chatId, "✅ Checking complete.", { reply_markup: getMainReplyKeyboard() });

    }
});
