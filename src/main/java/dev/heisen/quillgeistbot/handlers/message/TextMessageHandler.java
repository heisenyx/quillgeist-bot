package dev.heisen.quillgeistbot.handlers.message;

import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.model.Update;
import com.pengrad.telegrambot.model.request.ReplyParameters;
import com.pengrad.telegrambot.request.SendMessage;
import com.pengrad.telegrambot.request.SendVideo;
import dev.heisen.quillgeistbot.exception.UnsupportedResourceException;
import dev.heisen.quillgeistbot.exception.MaxFilesizeException;
import dev.heisen.quillgeistbot.service.FileService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.io.File;

@Component
@RequiredArgsConstructor
public class TextMessageHandler {

    private final TelegramBot bot;
    private final FileService fileService;

    public void handle(Update update) {

        String text = update.message().text();
        long chatId = update.message().chat().id();
        int messageId = update.message().messageId();

        if (text.contains("https")) {
            File file = null;
            try {
                file = fileService.downloadFile(update.message().text());

                SendVideo video = new SendVideo(chatId, file)
                        .replyParameters(new ReplyParameters(messageId));
                bot.execute(video);
            } catch (MaxFilesizeException e) {
                sendCallbackMessage(chatId, messageId, "File size limit reached");
            } catch (UnsupportedResourceException e) {
                sendCallbackMessage(chatId, messageId, "Unsupported resource");
            } catch (Exception e) {
                sendCallbackMessage(chatId, messageId, "Error");
            } finally {
                if (file != null) fileService.cleanup(file);
            }
        }
    }

    public void sendCallbackMessage(long chatId, int replyMessageId, String message) {
        SendMessage messageToSend = new SendMessage(chatId, message);
        messageToSend.replyParameters(new ReplyParameters(replyMessageId));
        bot.execute(messageToSend);
    }

    public void sendCallbackMessage(long chatId, String message) {
        SendMessage messageToSend = new SendMessage(chatId, message);
        bot.execute(messageToSend);
    }
}
