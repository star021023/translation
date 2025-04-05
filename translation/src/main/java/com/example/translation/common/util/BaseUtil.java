package com.example.translation.common.util;

import java.util.Random;

public class BaseUtil {
    public static String getRandomCode(int length) {
        StringBuilder sb = new StringBuilder();
        Random random = new Random();
        for (int i = 0; i < length; i++) {
            sb.append(random.nextInt(10)); // 生成0-9的随机数字
        }
        return sb.toString();
    }
}
