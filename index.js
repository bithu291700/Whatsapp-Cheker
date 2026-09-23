// WhatsApp Checker Bot - pairing/version fix for Railway
const crypto = require('crypto');
if (!global.crypto) global.crypto = crypto;

const {
    default: makeWASocket,
    useMultiFileAuthState,
    DisconnectReason,
    Browsers,
    makeCacheableSignalKeyStore,
    fetchLatestWaWebVersion
} = require('@whiskeysockets/baileys');

const TelegramBot = require('node-telegram-bot-api');
const express = require('express');
const fs = require('fs');
const path = require('path');
const pino = require('pino');

const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
const ADMIN_ID = 7388500439;
let currentPassword = "291736";

if (!TELEGRAM_TOKEN) {
    console.error("CRITICAL ERROR: TELEGRAM_TOKEN missing!");
    process.exit(1);
}

// Railway web server
const app = express();
const PORT = process.env.PORT || 8080;
app.get('/', (req, res) => res.status(200).send('WhatsApp Bot Active!'));
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server listening on port ${PORT}`);
});

const bot = new TelegramBot(TELEGRAM_TOKEN, { polling: true });

bot.on('polling_error', (err) => {
    console.error('Telegram polling error:', err?.message || err);
});
process.on('uncaughtException', (err) => console.error('Uncaught Exception:', err));
process.on('unhandledRejection', (reason) => console.error('Unhandled Rejection:', reason));

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
    return String(value || '').replace(/[^0-9]/g, '');
}

function isValidPhoneNumber(phone) {
    return /^\d{8,15}$/.test(phone);
}

async function getWhatsAppWebVersion() {
    try {
        // Use the live WhatsApp Web client revision.
        // This is important because stale bundled versions can generate a code
        // but fail when WhatsApp tries to finish the device link.
        const result = await fetchLatestWaWebVersion();
        if (result?.version?.length === 3) {
            console.log(
                `Using live WhatsApp Web version: ${result.version.join('.')} (latest=${result.isLatest})`
            );
            return result.version;
        }
    } catch (err) {
        console.error('Live WA Web version fetch failed:', err?.message || err);
    }

    // Do not invent a new version if the live lookup fails.
    // Let Baileys use its bundled version as a fallback.
    return undefined;
}

async function createWhatsAppConnection(chatId, phoneToPair = null) {
    const baseDir = path.join(__dirname, 'sessions');
    ensureDirExists(baseDir);

    const sessionDir = path.join(baseDir, `session_${chatId}`);

    // A new pairing request always starts from a clean auth state.
    if (phoneToPair) {
        if (userSockets[chatId]) {
            try {
                userSockets[chatId].end(undefined);
            } catch (_) {}
            delete userSockets[chatId];
        }

        if (fs.existsSync(sessionDir)) {
            try {
                fs.rmSync(sessionDir, { recursive: true, force: true });
            } catch (e) {
                console.error('Session cleanup error:', e);
            }
        }
    }

    ensureDirExists(sessionDir);

    const { state, saveCreds } = await useMultiFileAuthState(sessionDir);
    const waVersion = await getWhatsAppWebVersion();

    const socketOptions = {
        logger: pino({ level: 'info' }),
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
        retryRequestOnRetry: true,
        connectTimeoutMs: 60000,
        keepAliveIntervalMs: 25000
    };

    if (waVersion) {
        socketOptions.version = waVersion;
    }

    const waSock = makeWASocket(socketOptions);

    waSock.ev.on('creds.update', saveCreds);

    let codeRequested = false;

    const sendPairingCode = async () => {
        if (!phoneToPair || codeRequested || state.creds.registered) return;
        codeRequested = true;

        try {
            const cleanPhone = cleanPhoneNumber(phoneToPair);

            if (!isValidPhoneNumber(cleanPhone)) {
                codeRequested = false;
                await bot.sendMessage(
                    chatId,
                    "❌ Invalid WhatsApp number. Country code সহ শুধু digits দিন, যেমন `8801700000000`।",
                    { parse_mode: "Markdown", reply_markup: getMainReplyKeyboard() }
                );
                try { waSock.end(undefined); } catch (_) {}
                return;
            }

            // Give the socket a short moment to establish the initial handshake.
            await new Promise(resolve => setTimeout(resolve, 1500));

            if (state.creds.registered) return;

            const code = await waSock.requestPairingCode(cleanPhone);

            if (!code) {
                throw new Error('WhatsApp returned an empty pairing code');
            }

            const formattedCode = code.match(/.{1,4}/g)?.join("-") || code;

            await bot.sendMessage(
                chatId,
                `🔑 **Pairing Code:** \`${formattedCode}\`\n\n👉 WhatsApp → **Linked Devices** → **Link with phone number instead** → এই code দিন।`,
                {
                    parse_mode: "Markdown",
                    reply_markup: {
                        inline_keyboard: [
                            [{ text: "❌ Cancel Pairing", callback_data: "cancel_pairing" }]
                        ]
                    }
                }
            );
        } catch (err) {
            codeRequested = false;
            console.error('Pairing Request Error:', err);

            await bot.sendMessage(
                chatId,
                `❌ Pairing code তৈরি করা যায়নি.\n\nError: ${err?.message || 'Unknown error'}`,
                { reply_markup: getMainReplyKeyboard() }
            );

            try { waSock.end(undefined); } catch (_) {}
        }
    };

    waSock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        // requestPairingCode is triggered when WhatsApp sends the initial QR stage.
        // The QR itself is not shown to the Telegram user.
        if (phoneToPair && qr && !codeRequested && !state.creds.registered) {
            await sendPairingCode();
        }

        if (connection === 'open') {
            pairingInProgress[chatId] = false;

            if (!connectionNotified[chatId]) {
                connectionNotified[chatId] = true;

                await bot.sendMessage(
                    chatId,
                    "🎉 **WhatsApp Connected Successfully!**\n\nEhbar **📱 Check Number** option use koren.",
                    {
                        parse_mode: "Markdown",
                        reply_markup: getMainReplyKeyboard()
                    }
                );
            }
        }

        if (connection === 'close') {
            connectionNotified[chatId] = false;
            delete userSockets[chatId];
            pairingInProgress[chatId] = false;

            const statusCode =
                lastDisconnect?.error?.output?.statusCode ??
                lastDisconnect?.error?.statusCode;

            console.error('WhatsApp connection closed. Status:', statusCode);

            if (statusCode === DisconnectReason.loggedOut) {
                try {
                    fs.rmSync(sessionDir, { recursive: true, force: true });
                } catch (_) {}
            }

            if (
                phoneToPair &&
                [DisconnectReason.restartRequired, DisconnectReason.connectionClosed,
                 DisconnectReason.connectionLost, 408, 515].includes(statusCode)
            ) {
                console.log('Pairing/connection ended:', statusCode);
            }
        }
    });

    userSockets[chatId] = waSock;
    return waSock;
}

bot.on('callback_query', async (query) => {
    const chatId = query.message.chat.id;
    const data = query.data;

    if (data === "cancel_pairing") {
        delete userStates[chatId];
        pairingInProgress[chatId] = false;

        if (userSockets[chatId]) {
            try { userSockets[chatId].end(undefined); } catch (_) {}
            delete userSockets[chatId];
        }

        const sessionDir = path.join(__dirname, 'sessions', `session_${chatId}`);
        if (fs.existsSync(sessionDir)) {
            try {
                fs.rmSync(sessionDir, { recursive: true, force: true });
            } catch (_) {}
        }

        await bot.answerCallbackQuery(query.id, { text: "Pairing Cancelled!" });

        await bot.editMessageText("🚫 **Pairing attempt cancelled.**", {
            chat_id: chatId,
            message_id: query.message.message_id,
            parse_mode: "Markdown"
        });

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

        bot.sendMessage(chatId, "👋 **WhatsApp Checker Control Panel:**", {
            parse_mode: "Markdown",
            reply_markup: getMainReplyKeyboard()
        });
    } else {
        userStates[chatId] = "WAITING_FOR_PASSWORD";

        bot.sendMessage(chatId, "🔒 **Password Required!** Password din:");
    }
});

bot.on('message', async (msg) => {
    const chatId = msg.chat.id;
    const text = msg.text?.trim();

    if (!text || text.startsWith('/')) return;

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
                "⏳ Pairing already in progress. আগেরটা cancel করে আবার try করুন।"
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

        const isConnected =
            waSock &&
            (waSock.user || waSock.authState?.creds?.me || waSock.authState?.creds?.registered);

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

        const isConnected =
            waSock &&
            (waSock.user || waSock.authState?.creds?.me || waSock.authState?.creds?.registered)
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

        if (!isValidPhoneNumber(phone)) {
            return bot.sendMessage(
                chatId,
                "❌ Number ঠিক নয়। Country code সহ শুধু digits দিন। উদাহরণ: `8801700000000`",
                { parse_mode: "Markdown", reply_markup: getMainReplyKeyboard() }
            );
        }

        pairingInProgress[chatId] = true;

        await bot.sendMessage(chatId, "⏳ WebSocket Connection initialize hocche...");

        try {
            await createWhatsAppConnection(chatId, phone);
        } catch (err) {
            pairingInProgress[chatId] = false;
            console.error('createWhatsAppConnection error:', err);

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

        if (!isValidPhoneNumber(checkPhone)) {
            return bot.sendMessage(
                chatId,
                "❌ Invalid number.",
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
                    `📱 **Number:** \`+${checkPhone}\`\nSTATUS: ✅ **FRESH NUMBER**`,
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
                } catch (_) {}

                try {
                    statusBio = await waSock.fetchStatus(jid);
                } catch (_) {}

                const statusText =
                    (!profilePic && !statusBio)
                        ? "⚠️ **SEMI-FRESH**"
                        : "❌ **ACTIVE WHATSAPP ACCOUNT**";

                await bot.sendMessage(
                    chatId,
                    `📱 **Number:** \`+${checkPhone}\`\nSTATUS: ${statusText}\nBio: \`${statusBio?.status || "None"}\``,
                    {
                        parse_mode: "Markdown",
                        reply_markup: getMainReplyKeyboard()
                    }
                );
            }
        } catch (error) {
            console.error('Check failed:', error);

            await bot.sendMessage(
                chatId,
                "❌ Check failed.",
                { reply_markup: getMainReplyKeyboard() }
            );
        }
    }
});
