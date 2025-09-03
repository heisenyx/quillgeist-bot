package dev.heisen.quillgeistbot.bot;

import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.UpdatesListener;
import com.pengrad.telegrambot.model.Message;
import com.pengrad.telegrambot.model.Update;
import com.pengrad.telegrambot.request.SendMessage;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@RequiredArgsConstructor
@Slf4j
public class TelegramBotListener implements UpdatesListener {

    private final TelegramBot bot;

    @PostConstruct
    public void init() {
        bot.setUpdatesListener(this);
    }

    @Override
    public int process(List<Update> list) {
        list.forEach(update -> {
            log.info("Processing update {}", update);

            Message message = update.message();

            if (message != null && message.text() != null) {
                if (message.text().toLowerCase().contains("ping")) {
                    SendMessage response = new SendMessage(update.message().chat().username(), "pong");
                    bot.execute(response);
                }
            }
        });

        return UpdatesListener.CONFIRMED_UPDATES_ALL;
    }
}
