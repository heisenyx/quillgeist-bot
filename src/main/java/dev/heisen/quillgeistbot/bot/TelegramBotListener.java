package dev.heisen.quillgeistbot.bot;

import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.UpdatesListener;
import com.pengrad.telegrambot.model.Update;
import dev.heisen.quillgeistbot.dispatcher.UpdateDispatcher;
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
    private final UpdateDispatcher dispatcher;

    @PostConstruct
    public void init() {
        bot.setUpdatesListener(this);
    }

    @Override
    public int process(List<Update> list) {
        list.forEach(update -> {
            log.info("Processing update {}", update);

            try {
                dispatcher.dispatch(update);
            } catch (Exception e) {
                log.error("Error while dispatching update {}", update, e);
            }
        });

        return UpdatesListener.CONFIRMED_UPDATES_ALL;
    }
}