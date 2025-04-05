package com.example.translation.common.Interceptor;

import com.example.translation.common.result.ResultData;
import com.example.translation.common.result.ReturnCode;
import com.example.translation.common.util.JwtUtil;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.io.IOException;

@Component
public class JwtInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request,
                             HttpServletResponse response,
                             Object handler) throws Exception {
        String token = request.getHeader("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            sendError(response,  ReturnCode.RC401.getCode(), ReturnCode.RC401.getMessage());
            return false;
        }
        //提取并验证Token
        String jwt = token.substring(7);
        if (!JwtUtil.validateToken(jwt)) {
            sendError(response, ReturnCode.RC401.getCode(), ReturnCode.RC401.getMessage());
            return false;
        }
        //将用户信息存入请求属性
        Long userId = JwtUtil.getUserIdFromToken(jwt);
        request.setAttribute("userId", userId);
        UserContext.setUserId(userId); // 存入ThreadLocal
        return true;
    }

    private void sendError(HttpServletResponse response, int code, String msg) throws IOException {
        response.setStatus(code);
        response.setContentType("application/json");
        response.setCharacterEncoding("UTF-8");
        ResultData<?> resultData = ResultData.fail(code, msg);
        String jsonResponse = new ObjectMapper().writeValueAsString(resultData);
        response.getWriter().write(jsonResponse);
    }
    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        UserContext.clear(); // 请求结束后清理
    }
}
