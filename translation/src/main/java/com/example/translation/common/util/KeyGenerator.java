package com.example.translation.common.util;

import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import javax.crypto.SecretKey;
import java.util.Base64;

public class KeyGenerator {
    public static void main(String[] args) {
        // 生成一个符合 HS512 要求的密钥
        SecretKey key = Keys.secretKeyFor(SignatureAlgorithm.HS512);
        // 将密钥转换为 Base64 编码字符串
        String base64Key = Base64.getEncoder().encodeToString(key.getEncoded());
        System.out.println("Generated Key: " + base64Key);
    }
}
