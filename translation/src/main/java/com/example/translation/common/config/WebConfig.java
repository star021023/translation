package com.example.translation.common.config;

import com.example.translation.common.Interceptor.JwtInterceptor;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final JwtInterceptor jwtInterceptor;

    public WebConfig(JwtInterceptor jwtInterceptor) {
        this.jwtInterceptor = jwtInterceptor;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(jwtInterceptor)
                .addPathPatterns("/**")          // 拦截所有API接口
          .excludePathPatterns(                  //排除
                        "/login",                // 登录接口
                        "/register"  ,    // 注册接口
                        "/genRandom",
                        "/phoneLogin",
                        "/resetPassword"
                );
    }
}