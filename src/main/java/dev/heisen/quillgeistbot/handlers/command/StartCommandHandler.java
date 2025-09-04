package dev.heisen.quillgeistbot.handlers.command;

import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.model.Update;
import com.pengrad.telegrambot.model.request.InlineKeyboardButton;
import com.pengrad.telegrambot.model.request.InlineKeyboardMarkup;
import com.pengrad.telegrambot.request.SendMessage;
import org.springframework.stereotype.Component;

@Component
public class StartCommandHandler extends CommandHandler {

    public StartCommandHandler(TelegramBot bot) {
        super(bot);
    }

    @Override
    public void handle(Update update) {
        long chatId = update.message().chat().id();
        SendMessage message = new SendMessage(chatId, "Hey!");

        bot.execute(message);
    }

    @Override
    public String getCommand() {
        return "/start";
    }
}
