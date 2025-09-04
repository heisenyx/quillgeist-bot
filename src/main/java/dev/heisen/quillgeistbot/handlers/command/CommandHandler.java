package dev.heisen.quillgeistbot.handlers.command;

import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.model.Update;
import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
public abstract class CommandHandler {
    final TelegramBot bot;
    public abstract void handle(Update update);
    public abstract String getCommand();
}
