package dev.heisen.quillgeistbot.service;

import dev.heisen.quillgeistbot.config.YtDlpProperties;
import dev.heisen.quillgeistbot.exception.UnsupportedResourceException;
import dev.heisen.quillgeistbot.exception.MaxFilesizeException;
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
public class FileService {

    private final YtDlpProperties ytDlpProperties;

    public File downloadFile(String url) throws IOException, InterruptedException {
        log.info("Downloading file: {}", url);

        Path tempDir = Files.createTempDirectory("downloads-");

        String fileName = UUID.randomUUID() + "." + ytDlpProperties.getPreset();
        File outputFile = new File(tempDir.toFile(), fileName);

        ProcessBuilder processBuilder = new ProcessBuilder(
                "yt-dlp",
                "-o", outputFile.getAbsolutePath(),
                "-t", ytDlpProperties.getPreset(),
                "--max-filesize", ytDlpProperties.getMaxFilesize(),
                url
        );
        Process process = processBuilder.start();

        String processOutput;
        try (InputStream inputStream = process.getInputStream();
             InputStream errorStream = process.getErrorStream()
        ) {
            StringBuilder sb = new StringBuilder();
            sb.append(new String(inputStream.readAllBytes(), StandardCharsets.UTF_8));
            sb.append(new String(errorStream.readAllBytes(), StandardCharsets.UTF_8));
            processOutput = sb.toString();
        }

        int exitCode = process.waitFor();

        if (processOutput.contains("max-filesize")) {
            log.info("File size limit reached for URL: {}", url);
            cleanup(outputFile);
            throw new MaxFilesizeException(processOutput);
        } else if (processOutput.contains("Unsupported")) {
            log.info("Unsupported resource with url: {}", url);
            cleanup(outputFile);
            throw new UnsupportedResourceException(processOutput);
        } else if (exitCode == 0 && outputFile.exists()) {
            log.info("File downloaded successfully: {}", outputFile.getAbsolutePath());
            return outputFile;
        } else {
            log.error("File download failed. Exit code: {} Process output: {}", exitCode, processOutput);
            cleanup(outputFile);
            throw new IOException("File download failed with exit code: " + exitCode);
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