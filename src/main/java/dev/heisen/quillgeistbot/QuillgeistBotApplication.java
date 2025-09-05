package dev.heisen.quillgeistbot;

import dev.heisen.quillgeistbot.config.BotConfig;
import dev.heisen.quillgeistbot.config.YtDlpProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties({
        BotConfig.class,
        YtDlpProperties.class

})
public class QuillgeistBotApplication {

    public static void main(String[] args) {
        SpringApplication.run(QuillgeistBotApplication.class, args);
    }

}
