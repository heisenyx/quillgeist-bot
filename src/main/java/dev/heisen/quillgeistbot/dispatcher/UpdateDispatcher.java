package dev.heisen.quillgeistbot.dispatcher;

import com.pengrad.telegrambot.model.Update;
import dev.heisen.quillgeistbot.handlers.command.CommandHandler;
import dev.heisen.quillgeistbot.handlers.message.TextMessageHandler;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

@Component
public class UpdateDispatcher {

    private final Map<String, CommandHandler> commandsMap;
    private final TextMessageHandler textMessageHandler;

    public UpdateDispatcher(List<CommandHandler> commandsMap, TextMessageHandler textMessageHandler) {
        this.commandsMap = commandsMap.stream()
                .collect(Collectors.toMap(CommandHandler::getCommand, Function.identity()));
        this.textMessageHandler = textMessageHandler;
    }

    public void dispatch(Update update) {
        if (update.message() != null) {
            handleMessage(update);
        }
    }

    private void handleMessage(Update update) {
        if (update.message().text() == null) return;

        String command = update.message().text().split("[ @]")[0];
        CommandHandler commandHandler = commandsMap.get(command);

        if (commandHandler != null) {
            commandHandler.handle(update);
        } else {
            textMessageHandler.handle(update);
        }
    }
}
