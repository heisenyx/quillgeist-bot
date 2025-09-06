package dev.heisen.quillgeistbot.config;

import jakarta.validation.constraints.NotEmpty;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "yt-dlp")
@Getter
@RequiredArgsConstructor
public class YtDlpProperties {

    @NotEmpty
    private final String preset;

    @NotEmpty
    private final String maxFilesize;
}
