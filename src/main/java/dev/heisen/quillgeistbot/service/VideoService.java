package dev.heisen.quillgeistbot.service;

import dev.heisen.quillgeistbot.config.YtDlpProperties;
import dev.heisen.quillgeistbot.exception.VideoMaxFilesizeException;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.util.FileSystemUtils;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;

@Service
@Slf4j
@RequiredArgsConstructor
public class VideoService {

    private final YtDlpProperties ytDlpProperties;

    public File downloadVideo(String url) throws IOException, InterruptedException {
        log.info("Downloading video: {}", url);

        Path tempDir = Files.createTempDirectory("video-downloads-");

        String fileName = UUID.randomUUID() + "." + ytDlpProperties.getFormat();
        File outputFile = new File(tempDir.toFile(), fileName);

        ProcessBuilder processBuilder = new ProcessBuilder(
                "yt-dlp",
                "-o", outputFile.getAbsolutePath(),
                "--format", ytDlpProperties.getFormat(),
                "--max-filesize", ytDlpProperties.getMaxFilesize(),
                url
        );
        Process process = processBuilder.start();

        String processOutput;
        try (InputStream inputStream = process.getInputStream()) {
            processOutput = new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
        }

        String errorOutput;
        try (InputStream errorStream = process.getErrorStream()) {
            errorOutput = new String(errorStream.readAllBytes(), StandardCharsets.UTF_8);
        }

        int exitCode = process.waitFor();

        if (processOutput.contains("File is larger than max-filesize")) {
            log.warn("Video size limit reached for URL: {}. Process output: {}", url, processOutput);
            throw new VideoMaxFilesizeException(processOutput);
        } else if (exitCode == 0 && outputFile.exists() && outputFile.length() > 0) {
            log.info("Video downloaded successfully: {}", outputFile.getAbsolutePath());
            return outputFile;
        } else {
            log.error("Error downloading video. Exit code: {}. Process output: {}. Error message: {}", exitCode, processOutput, errorOutput);
            cleanup(outputFile);
            throw new IOException("Video download failed with exit code: " + exitCode);
        }
    }

    public void cleanup(File file) {
        Path path = file.getParentFile().toPath();
        try {
            FileSystemUtils.deleteRecursively(path);
        } catch (IOException e) {
            log.error("Failed to clean up temporary files", e);
        }
    }
}