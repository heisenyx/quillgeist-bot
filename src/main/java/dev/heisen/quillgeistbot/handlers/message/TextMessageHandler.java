package dev.heisen.quillgeistbot.handlers.message;

import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.model.Update;
import com.pengrad.telegrambot.request.SendVideo;
import dev.heisen.quillgeistbot.service.VideoService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.File;

@Slf4j
@Component
@RequiredArgsConstructor
public class TextMessageHandler {

    private final TelegramBot bot;
    private final VideoService videoService;

    public void handle(Update update) {
        if (update.message().text().contains("https")) {
            long chatId = update.message().chat().id();

            File file = null;
            try {
                file = videoService.downloadVideo(update.message().text());

                SendVideo video = new SendVideo(chatId, file);
                bot.execute(video);
            } catch (Exception e) {
                log.error("Error downloading video", e);
            } finally {
                if (file != null) videoService.cleanup(file);
            }
        }
    }
}
