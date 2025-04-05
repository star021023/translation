package com.example.translation.common.util;

import io.jsonwebtoken.*;
import jakarta.annotation.PostConstruct;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.Date;
@Slf4j
@Component
public class JwtUtil {
    @Value("${jwt.secret-key}")
    private String secretKey;
    @PostConstruct
    public void init() {
        SECRET_KEY = secretKey;
    }
    private static String SECRET_KEY; // 静态字段
    private static final long EXPIRATION_TIME = 864_000_000; //10天

    public static String generateToken(Long userId, String username) {
        return Jwts.builder()
                .setSubject(username)
                .claim("userId", userId)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + EXPIRATION_TIME))
                .signWith(SignatureAlgorithm.HS512, SECRET_KEY)
                .compact();
    }

    public static boolean validateToken(String token) {
        try {
            // 解析Token时会自动验证签名和过期时间
            Jwts.parserBuilder()
                    .setSigningKey(SECRET_KEY)
                    .build()
                    .parseClaimsJws(token);
            return true;
        } catch (ExpiredJwtException ex) {
            log.error("Token已过期: {}", ex.getMessage());
        } catch (UnsupportedJwtException ex) {
            log.error("Token格式错误: {}", ex.getMessage());
        } catch (MalformedJwtException ex) {
            log.error("Token结构损坏: {}", ex.getMessage());
        } catch (SignatureException ex) {
            log.error("签名验证失败: {}", ex.getMessage());
        } catch (IllegalArgumentException ex) {
            log.error("空Token或非法参数: {}", ex.getMessage());
        }
        return false;
    }
    public static Long getUserIdFromToken(String token) {
        Claims claims = Jwts.parserBuilder()
                .setSigningKey(SECRET_KEY)
                .build()
                .parseClaimsJws(token)
                .getBody();
        return claims.get("userId", Long.class); // 从自定义claim获取用户ID
    }

}