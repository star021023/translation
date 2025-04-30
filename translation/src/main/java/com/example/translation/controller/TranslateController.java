package com.example.translation.controller;
import com.example.translation.common.result.ResultData;
import com.example.translation.pojo.dto.DataChunk;
import com.example.translation.pojo.dto.TranslateRequestDTO;

import com.example.translation.service.TranslateService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;

@RestController
@RequestMapping("/translate")
public class TranslateController {
    @Autowired
    private TranslateService translateService;

    @PostMapping(produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<ResultData<DataChunk>>> translate(@RequestBody TranslateRequestDTO dto, HttpServletRequest request) {
        return translateService.translate(dto,request)
                .map(sse -> {
                    ResultData<DataChunk> result = ResultData.success(sse.data());
                    return ServerSentEvent.<ResultData<DataChunk>>builder()
                            .data(result)
                            .event(sse.event())
                            .build();
                })
                .onErrorResume(e -> Flux.just(
                        ServerSentEvent.builder(ResultData.<DataChunk>fail(500, e.getMessage())).build()
                ));
    }

    @GetMapping("/blueScore")
    public  ResultData<String> bleuScore(@RequestParam String reference,@RequestParam String candidate){
        return translateService.blueScore(reference,candidate);
    }

    @GetMapping("/chart")
    public ResultData bleuScoreChart(){
        return translateService.bleuScoreChart();
    }

    @PostMapping("/refresh")
    public ResultData reFresh(){
        return translateService.refreshChart();
    }
}

