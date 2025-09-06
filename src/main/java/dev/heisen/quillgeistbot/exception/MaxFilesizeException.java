package dev.heisen.quillgeistbot.exception;

public class MaxFilesizeException extends RuntimeException {
    public MaxFilesizeException(String message) {
        super(message);
    }
}
