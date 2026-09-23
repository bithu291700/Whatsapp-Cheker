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

function getMainReplyKeyboard() {
    return {
        keyboard: [
            [{ text: "🔢 Pair via Code" }],
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

async function createWhatsAppConnection(chatId, phoneToPair = null) {
    const baseDir = path.join(__dirname, 'sessions');
    ensureDirExists(baseDir);

    const sessionDir = path.join(baseDir, `session_${chatId}`);

    // A new phone pairing always starts with a clean auth state.
    if (phoneToPair) {
        await destroySocket(chatId, true);
    }

    ensureDirExists(sessionDir);

    const { state, saveCreds } = await useMultiFileAuthState(sessionDir);

    // Fetch the current WA Web version when supported by the installed Baileys.
    const latestVersion = await getLatestVersionIfAvailable();

    const socketConfig = {
        logger: pino({ level: 'warn' }),

        // IMPORTANT: use a canonical browser identity for pairing.
        browser: Browsers.ubuntu('Chrome'),

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

    if (latestVersion) {
        socketConfig.version = latestVersion;
    }

    const waSock = makeWASocket(socketConfig);

    userSockets[chatId] = waSock;
    waSock.ev.on('creds.update', saveCreds);

    let codeRequested = false;
    let pairingMessageSent = false;

    const requestCode = async () => {
        if (!phoneToPair || codeRequested || state.creds.registered) {
            return;
        }

        codeRequested = true;

        try {
            const cleanPhone = cleanPhoneNumber(phoneToPair);

            if (!isValidInternationalNumber(cleanPhone)) {
                throw new Error(
                    "Invalid phone number. Use country code + digits only, e.g. 8801700000000"
                );
            }

            console.log(`Requesting pairing code for ${cleanPhone}`);

            // Give the socket a short moment to establish the initial WA connection.
            await new Promise(resolve => setTimeout(resolve, 1500));

            const rawCode = await waSock.requestPairingCode(cleanPhone);

            if (!rawCode) {
                throw new Error("WhatsApp returned an empty pairing code.");
            }

            const code = rawCode.match(/.{1,4}/g)?.join("-") || rawCode;

            pairingMessageSent = true;

            await bot.sendMessage(
                chatId,
                `🔑 **Pairing Code:** \`${code}\`\n\n` +
                `👉 WhatsApp → Linked Devices → Link with phone number instead → code দিন।\n\n` +
                `⚠️ Codeটি নতুন করে generate করা হয়েছে; পুরোনো code ব্যবহার করবেন না।`,
                {
                    parse_mode: "Markdown",
                    reply_markup: {
                        inline_keyboard: [
                            [{ text: "❌ Cancel Pairing", callback_data: "cancel_pairing" }]
                        ]
                    }
                }
            );

            console.log(`Pairing code sent to Telegram chat ${chatId}`);
        } catch (err) {
            console.error("Pairing Request Error:", err);

            codeRequested = false;
            pairingMessageSent = false;

            await bot.sendMessage(
                chatId,
                `❌ Pairing code তৈরি করা যায়নি.\n\nError: ${err?.message || 'Unknown error'}`,
                { reply_markup: getMainReplyKeyboard() }
            );

            pairingInProgress[chatId] = false;
        }
    };

    waSock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;
        const statusCode = getStatusCode(lastDisconnect);

        console.log(
            `WA connection update [${chatId}]: connection=${connection || '-'} status=${statusCode || '-'} qr=${!!qr}`
        );

        // For pairing-code flow, QR is not displayed. It is used only as a
        // signal that the initial companion session is ready.
        if (
            phoneToPair &&
            !codeRequested &&
            !state.creds.registered &&
            qr
        ) {
            await requestCode();
        }

        // Fallback: some Baileys versions do not emit QR before pairing.
        // Don't wait forever for it.
        if (
            phoneToPair &&
            !codeRequested &&
            !state.creds.registered &&
            !qr
        ) {
            setTimeout(() => {
                requestCode().catch(err => {
                    console.error("Pairing fallback error:", err);
                });
            }, 2500);
        }

        if (connection === 'open') {
            pairingInProgress[chatId] = false;
            connectionNotified[chatId] = true;

            await bot.sendMessage(
                chatId,
                "🎉 **WhatsApp Connected Successfully!**\n\n" +
                "Ehbar **📱 Check Number** option use koren.",
                {
                    parse_mode: "Markdown",
                    reply_markup: getMainReplyKeyboard()
                }
            );
        }

        if (connection === 'close') {
            connectionNotified[chatId] = false;

            const wasPairing = Boolean(phoneToPair && !state.creds.registered);

            delete userSockets[chatId];

            console.error(
                `WhatsApp connection closed [${chatId}], status=${statusCode || 'unknown'}`
            );

            // 515/408/connectionClosed can happen during a failed pairing.
            // Don't loop endlessly because repeated requests can trigger rate limits.
            if (wasPairing && [408, 515, 428, 503].includes(Number(statusCode))) {
                pairingInProgress[chatId] = false;

                await bot.sendMessage(
                    chatId,
                    `❌ WhatsApp pairing rejected the connection (code ${statusCode}).\n\n` +
                    `এই code আর ব্যবহার করবেন না। আবার **🔢 Pair via Code** চাপুন এবং নতুন code নিন।`,
                    { reply_markup: getMainReplyKeyboard() }
                );

                return;
            }

            if (statusCode === DisconnectReason.loggedOut) {
                try {
                    fs.rmSync(sessionDir, { recursive: true, force: true });
                } catch (e) {}
            }
        }
    });

    // If QR event is never emitted, request pairing code through the fallback.
    if (phoneToPair && !state.creds.registered) {
        setTimeout(() => {
            requestCode().catch(err => {
                console.error("Initial pairing fallback error:", err);
            });
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

        if (!waSock) {
            return bot.sendMessage(
                chatId,
                "⚠️ WhatsApp connect kora nei!",
                { reply_markup: getMainReplyKeyboard() }
            );
        }

        const checkPhone = cleanPhoneNumber(text);

        if (!isValidInternationalNumber(checkPhone)) {
            return bot.sendMessage(
                chatId,
                "❌ Number ভুল। Country code সহ শুধু digits দিন।",
                { reply_markup: getMainReplyKeyboard() }
            );
        }

        const jid = `${checkPhone}@s.whatsapp.net`;

        await bot.sendMessage(
            chatId,
            `⏳ \`+${checkPhone}\` checking...`,
            { parse_mode: "Markdown" }
        );

        try {
            const [result] = await waSock.onWhatsApp(checkPhone);

            if (!result || !result.exists) {
                await bot.sendMessage(
                    chatId,
                    `📱 **Number:** \`+${checkPhone}\`\n` +
                    `STATUS: ✅ **FRESH NUMBER**\n` +
                    `Send Success Chance: **95%**`,
                    {
                        parse_mode: "Markdown",
                        reply_markup: getMainReplyKeyboard()
                    }
                );
            } else {
                let profilePic = null;
                let statusBio = null;

                try {
                    profilePic = await waSock.profilePictureUrl(jid, 'image');
                } catch (e) {}

                try {
                    statusBio = await waSock.fetchStatus(jid);
                } catch (e) {}

                const statusText =
                    (!profilePic && !statusBio)
                        ? "⚠️ **SEMI-FRESH (75% Delivery Rate)**"
                        : "❌ **ACTIVE WHATSAPP ACCOUNT**";

                await bot.sendMessage(
                    chatId,
                    `📱 **Number:** \`+${checkPhone}\`\n` +
                    `STATUS: ${statusText}\n` +
                    `Bio: \`${statusBio?.status || "None"}\``,
                    {
                        parse_mode: "Markdown",
                        reply_markup: getMainReplyKeyboard()
                    }
                );
            }
        } catch (error) {
            console.error("Check failed:", error);

            await bot.sendMessage(
                chatId,
                "❌ Check failed.",
                { reply_markup: getMainReplyKeyboard() }
            );
        }
    }
});
