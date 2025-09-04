package dev.heisen.quillgeistbot.handlers.command;

import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.model.Update;
import com.pengrad.telegrambot.model.request.InlineKeyboardButton;
import com.pengrad.telegrambot.model.request.InlineKeyboardMarkup;
import com.pengrad.telegrambot.request.SendMessage;
import org.springframework.stereotype.Component;

@Component
public class SettingsCommandHandler extends CommandHandler {

    public SettingsCommandHandler(TelegramBot bot) {
        super(bot);
    }

    @Override
    public void handle(Update update) {
        long chatId = update.message().chat().id();

        InlineKeyboardMarkup inlineKeyboard = new InlineKeyboardMarkup(
                new InlineKeyboardButton[]{
                        new InlineKeyboardButton("Button1").url("google.com")
                },
                new InlineKeyboardButton[]{
                        new InlineKeyboardButton("Button2").callbackData("google.com"),
                        new InlineKeyboardButton("Button3").switchInlineQuery("google.com")
                }
        );
        SendMessage message = new SendMessage(chatId, "Test settings");
        message.setReplyMarkup(inlineKeyboard);

        bot.execute(message);
    }

    @Override
    public String getCommand() {
        return "/settings";
    }
}
