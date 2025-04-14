package com.example.translation.service;

import com.example.translation.common.result.ResultData;
import com.example.translation.pojo.dto.DataChunk;
import com.example.translation.pojo.dto.ImgTranslDTO;
import com.example.translation.pojo.dto.TranslateRequestDTO;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.codec.ServerSentEvent;
import reactor.core.publisher.Flux;


public interface TranslateService {

    Flux<ServerSentEvent<DataChunk>> translate(TranslateRequestDTO dto, HttpServletRequest request);

    Flux<ServerSentEvent<DataChunk>> imgTranslate(ImgTranslDTO imgTranslDTO);
}
