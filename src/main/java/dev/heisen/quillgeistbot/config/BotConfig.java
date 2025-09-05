package dev.heisen.quillgeistbot.config;

import com.pengrad.telegrambot.TelegramBot;
import jakarta.validation.constraints.NotEmpty;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.validation.annotation.Validated;

@ConfigurationProperties(prefix = "bot")
@Validated
@RequiredArgsConstructor
public class BotConfig {

    @NotEmpty
    private final String token;

    @Bean
    public TelegramBot telegramBot() {
        return new TelegramBot.Builder(token)
                .build();
    }
}
