const { 
    default: makeWASocket, 
    useMultiFileAuthState, 
    DisconnectReason, 
    Browsers,
    makeCacheableSignalKeyStore
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

const app = express();
const PORT = process.env.PORT || 8080;
app.get('/', (req, res) => res.status(200).send('WhatsApp Bot Active!'));
app.listen(PORT, '0.0.0.0', () => console.log(`Server listening on port ${PORT}`));

const bot = new TelegramBot(TELEGRAM_TOKEN, { polling: true });

bot.on('polling_error', (err) => {});
process.on('uncaughtException', (err) => console.error('Uncaught Exception:', err));
process.on('unhandledRejection', (reason) => console.error('Unhandled Rejection:', reason));

const userSockets = {};
const userStates = {};
const authenticatedUsers = new Set(); 
const connectionNotified = {}; 

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

async function createWhatsAppConnection(chatId, phoneToPair = null) {
    const baseDir = path.join(__dirname, 'sessions');
    ensureDirExists(baseDir);
    const sessionDir = path.join(baseDir, `session_${chatId}`);

    if (phoneToPair) {
        if (userSockets[chatId]) {
            try { userSockets[chatId].end(undefined); } catch (e) {}
            delete userSockets[chatId];
        }
        if (fs.existsSync(sessionDir)) {
            try { fs.rmSync(sessionDir, { recursive: true, force: true }); } catch (e) {}
        }
    }

    ensureDirExists(sessionDir);
    const { state, saveCreds } = await useMultiFileAuthState(sessionDir);

    const waSock = makeWASocket({
        logger: pino({ level: 'fatal' }),
        browser: Browsers.ubuntu('Chrome'),
        auth: {
            creds: state.creds,
            keys: makeCacheableSignalKeyStore(state.keys, pino({ level: 'fatal' }))
        },
        markOnlineOnConnect: false,
        syncFullHistory: false
    });

    waSock.ev.on('creds.update', saveCreds);

    let codeRequested = false;

    // Correct Baileys Pairing Code Pattern: Trigger requestPairingCode on 'qr' event
    waSock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (phoneToPair && qr && !codeRequested && !waSock.authState.creds.registered) {
            codeRequested = true;
            try {
                const cleanPhone = phoneToPair.toString().replace(/[^0-9]/g, '');
                let code = await waSock.requestPairingCode(cleanPhone);
                code = code?.match(/.{1,4}/g)?.join("-") || code;

                bot.sendMessage(chatId, `🔑 **Pairing Code:** \`${code}\`\n\n👉 Apnar WhatsApp-er **Linked Devices > Link with Phone Number Instead**-e giye ekhon code-ti bosiye din!`, {
                    parse_mode: "Markdown",
                    reply_markup: {
                        inline_keyboard: [
                            [{ text: "❌ Cancel Pairing", callback_data: "cancel_pairing" }]
                        ]
                    }
                });
            } catch (err) {
                console.error("Pairing Request Error:", err);
                bot.sendMessage(chatId, "❌ Pairing Request Failed! Abar try koren.", { reply_markup: getMainReplyKeyboard() });
            }
        }

        if (connection === 'open') {
            if (!connectionNotified[chatId]) {
                connectionNotified[chatId] = true;
                bot.sendMessage(chatId, "🎉 **WhatsApp Connected Successfully!**\n\nEhbar **📱 Check Number** option use koren.", {
                    parse_mode: "Markdown",
                    reply_markup: getMainReplyKeyboard()
                });
            }
        } else if (connection === 'close') {
            connectionNotified[chatId] = false;
            delete userSockets[chatId];
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            if (statusCode === DisconnectReason.loggedOut) {
                try { fs.rmSync(sessionDir, { recursive: true, force: true }); } catch (e) {}
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

        if (userSockets[chatId]) {
            try { userSockets[chatId].end(undefined); } catch (e) {}
            delete userSockets[chatId];
        }

        const sessionDir = path.join(__dirname, 'sessions', `session_${chatId}`);
        if (fs.existsSync(sessionDir)) {
            try { fs.rmSync(sessionDir, { recursive: true, force: true }); } catch (e) {}
        }

        await bot.answerCallbackQuery(query.id, { text: "Pairing Cancelled!" });
        await bot.editMessageText("🚫 **Pairing attempt cancelled.**", {
            chat_id: chatId,
            message_id: query.message.message_id,
            parse_mode: "Markdown"
        });

        bot.sendMessage(chatId, "Main menu-te firiye neya holo:", { reply_markup: getMainReplyKeyboard() });
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
            return bot.sendMessage(chatId, "🎉 Access Granted!", { reply_markup: getMainReplyKeyboard() });
        } else {
            return bot.sendMessage(chatId, "❌ Bhul Password!");
        }
    }

    if (text === "🔢 Pair via Code") {
        userStates[chatId] = "WAITING_FOR_LINK_NUMBER";
        return bot.sendMessage(chatId, "📲 WhatsApp Number (Country Code সহ, e.g. `8801700000000`):", { parse_mode: "Markdown" });
    } 
    
    if (text === "📱 Check Number") {
        const waSock = userSockets[chatId];
        const isConnected = waSock && (waSock.user || waSock.authState?.creds?.me || waSock.authState?.creds?.registered);

        if (!isConnected) {
            return bot.sendMessage(chatId, "⚠️ Prothome **🔢 Pair via Code** koren!", { reply_markup: getMainReplyKeyboard() });
        }
        userStates[chatId] = "WAITING_FOR_CHECK_NUMBER";
        return bot.sendMessage(chatId, "🔍 Number din (e.g. `8801800000000`):", { parse_mode: "Markdown" });
    } 

    if (text === "ℹ️ Help & Status") {
        const waSock = userSockets[chatId];
        const isConnected = waSock && (waSock.user || waSock.authState?.creds?.me || waSock.authState?.creds?.registered) ? "✅ Connected" : "❌ Not Connected";
        return bot.sendMessage(chatId, `ℹ️ **Status:** ${isConnected}`, { reply_markup: getMainReplyKeyboard() });
    }

    const state = userStates[chatId];

    if (state === "WAITING_FOR_LINK_NUMBER") {
        delete userStates[chatId];
        const phone = text.replace(/[^0-9]/g, '');

        bot.sendMessage(chatId, "⏳ WebSocket Connection initialize hocche...");
        await createWhatsAppConnection(chatId, phone);

    } else if (state === "WAITING_FOR_CHECK_NUMBER") {
        delete userStates[chatId];
        const waSock = userSockets[chatId];

        if (!waSock) {
            return bot.sendMessage(chatId, "⚠️ WhatsApp connect kora nei!", { reply_markup: getMainReplyKeyboard() });
        }

        const checkPhone = text.replace(/[^0-9]/g, '');
        const jid = `${checkPhone}@s.whatsapp.net`;
        bot.sendMessage(chatId, `⏳ \`+${checkPhone}\` checking...`, { parse_mode: "Markdown" });

        try {
            const [result] = await waSock.onWhatsApp(checkPhone);

            if (!result || !result.exists) {
                bot.sendMessage(chatId, `📱 **Number:** \`+${checkPhone}\`\nSTATUS: ✅ **FRESH NUMBER**\nSend Success Chance: **95%**`, { parse_mode: "Markdown", reply_markup: getMainReplyKeyboard() });
            } else {
                let profilePic = null, statusBio = null;
                try { profilePic = await waSock.profilePictureUrl(jid, 'image'); } catch (e) {}
                try { statusBio = await waSock.fetchStatus(jid); } catch (e) {}

                let statusText = (!profilePic && !statusBio) ? "⚠️ **SEMI-FRESH (75% Delivery Rate)**" : "❌ **ACTIVE WHATSAPP ACCOUNT**";

                bot.sendMessage(chatId, `📱 **Number:** \`+${checkPhone}\`\nSTATUS: ${statusText}\nBio: \`${statusBio?.status || "None"}\``, { parse_mode: "Markdown", reply_markup: getMainReplyKeyboard() });
            }
        } catch (error) {
            bot.sendMessage(chatId, "❌ Check failed.", { reply_markup: getMainReplyKeyboard() });
        }
    }
});
