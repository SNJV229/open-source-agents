package com.example.service.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.Instant;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getUserById(@PathVariable("id") String id) {
        return ResponseEntity.ok(Map.of(
            "accountNumber", id,
            "email", "user@example.com",
            "accountStatus", "ACTIVE",
            "lastLoginTimestamp", Instant.now().toEpochMilli()
        ));
    }

    @PatchMapping("/{id}")
    public ResponseEntity<Void> updateUserPartial(@PathVariable("id") String id, @RequestBody Map<String, Object> updates) {
        return ResponseEntity.noContent().build();
    }
}