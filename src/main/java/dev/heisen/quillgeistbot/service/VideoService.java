package dev.heisen.quillgeistbot.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.util.FileSystemUtils;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;

@Service
@Slf4j
public class VideoService {

    public File downloadVideo(String url) throws IOException, InterruptedException {
        log.info("Downloading video: {}", url);

        Path tempDir = Files.createTempDirectory("video-downloads-");

        String fileName = UUID.randomUUID() + ".mp4";
        File outputFile = new File(tempDir.toFile(), fileName);

        ProcessBuilder processBuilder = new ProcessBuilder(
                "yt-dlp",
                "-o", outputFile.getAbsolutePath(),
                "--format", "mp4",
                url
        );
        Process process = processBuilder.start();
        int exitCode = process.waitFor();

        if (exitCode == 0 && outputFile.exists()) {
            log.info("Video downloaded successfully: {}", outputFile.getAbsolutePath());
            return outputFile;
        } else {
            throw new IOException("Video download failed");
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
