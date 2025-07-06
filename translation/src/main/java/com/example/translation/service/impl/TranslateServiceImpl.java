package com.example.translation.service.impl;

import com.example.translation.common.Interceptor.UserContext;
import com.example.translation.common.result.ResultData;
import com.example.translation.mapper.BleuResultMapper;
import com.example.translation.mapper.DocHistoryMapper;
import com.example.translation.mapper.HistoryMapper;
import com.example.translation.mapper.ImgHistoryMapper;
import com.example.translation.pojo.dto.DataChunk;
import com.example.translation.pojo.dto.ImgTranslDTO;
import com.example.translation.pojo.dto.TranslateRequestDTO;
import com.example.translation.pojo.po.DocHistory;
import com.example.translation.pojo.po.History;
import com.example.translation.pojo.po.ImgHistory;
import com.example.translation.service.TranslateService;
import io.netty.channel.ChannelOption;
import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.client.ReactorResourceFactory;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;
import reactor.netty.http.client.HttpClient;
import reactor.netty.resources.ConnectionProvider;

import java.time.Duration;
import java.util.List;
import java.util.Map;
@Slf4j
@Service
public class TranslateServiceImpl implements TranslateService {
    @Autowired
    private HistoryMapper historyMapper;
    @Autowired
    private BleuResultMapper bleuResultMapper;
    @Autowired
    private ImgHistoryMapper imgHistoryMapper;
    @Autowired
    private DocHistoryMapper docHistoryMapper;
    private final WebClient webClient;

    public TranslateServiceImpl(WebClient.Builder webClientBuilder) {
        // 创建连接池资源工厂
        ReactorResourceFactory resourceFactory = new ReactorResourceFactory();
        resourceFactory.setUseGlobalResources(false); // 禁用全局资源，避免干扰其他服务

        // 配置连接池参数
        ConnectionProvider connectionProvider = ConnectionProvider.builder("flask-connection-pool")
                .maxConnections(100)                 // 全局最大连接数
                .pendingAcquireTimeout(Duration.ofMillis(450000)) // 获取连接超时时间
                .maxIdleTime(Duration.ofMillis(300000)) // 空闲连接超时释放
                .build();

        // 构建 HttpClient
        HttpClient httpClient = HttpClient.create(connectionProvider)
                .responseTimeout(Duration.ofSeconds(300))  // 响应超时时间
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 50000); // 连接超时时间

        this.webClient = webClientBuilder
                .baseUrl("http://127.0.0.1:5000")
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .codecs(configurer -> configurer
                        .defaultCodecs()
                        .maxInMemorySize(256 * 1024)
                )
                .build();
    }
    @Override
    public Flux<ServerSentEvent<DataChunk>> translate(TranslateRequestDTO dto, HttpServletRequest request) {
        Long userId = (Long) request.getAttribute("userId");
        // 定义两个缓冲区分别存储不同阶段内容
        StringBuilder targetText = new StringBuilder();
        StringBuilder reflect = new StringBuilder();
        StringBuilder reflectText = new StringBuilder();
        return webClient.post()
                .uri("/translation")
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.TEXT_EVENT_STREAM)
                .bodyValue(buildRequestBody(dto))
                .retrieve()
                .bodyToFlux(DataChunk.class)
                .doOnNext(chunk -> {
                    switch (chunk.getStage()) {
                        case "first" -> targetText.append(chunk.getChunk());
                        case "reflect" -> reflect.append(chunk.getChunk());
                        case "improve" -> reflectText.append(chunk.getChunk());
                    }
                })
                .map(chunk -> ServerSentEvent.builder(chunk).build())
                .doOnComplete(() -> saveHistory(
                        dto,
                        targetText.toString(),
                        reflect.toString(),
                        reflectText.toString(),
                        userId
                ));
    }
    @Override
    public Flux<ServerSentEvent<DataChunk>> imgTranslate(ImgTranslDTO imgTranslDTO) {
        Long userId = UserContext.getUserId();
        // 定义两个缓冲区分别存储不同阶段内容
        StringBuilder sourceText = new StringBuilder();
        StringBuilder targetText = new StringBuilder();
        StringBuilder reflect = new StringBuilder();
        StringBuilder reflectText = new StringBuilder();
        return webClient.post()
                .uri("/imgTransl")
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.TEXT_EVENT_STREAM)
                .bodyValue(buildImgRequestBody(imgTranslDTO))
                .retrieve()
                .bodyToFlux(DataChunk.class)
                .filter(chunk -> chunk != null) // 过滤null值
                .doOnNext(chunk -> {
                    String stage = chunk.getStage() != null ? chunk.getStage() : "unknown";
                    String content = chunk.getChunk() != null ? chunk.getChunk() : "";
                    switch (stage) {
                        case "source" -> sourceText.append(content);
                        case "first" -> targetText.append(content);
                        case "reflect" -> reflect.append(content);
                        case "improve" -> reflectText.append(content);
                    }
                })
                .map(chunk -> ServerSentEvent.builder(chunk).build())
                .doOnComplete(() ->  saveImgHistory(
                        imgTranslDTO,
                        sourceText.toString(),
                        targetText.toString(),
                        reflect.toString(),
                        reflectText.toString(),
                        userId
                ));
    }
    @Override
    public ResultData<String> docTranslate(ImgTranslDTO imgTranslDTO, String originalFilename) {
        Long userId = UserContext.getUserId();
        return webClient.post()
                .uri("/wordTransl")
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.APPLICATION_JSON)
                .bodyValue(buildImgRequestBody(imgTranslDTO))
                .retrieve()
                .bodyToMono(String.class)
                .map(filename -> {
                    // 构建完整的下载URL
                    String downloadUrl = "http://127.0.0.1:5000/download?filename=" + filename;
                    saveDocHistory(
                            originalFilename,
                            downloadUrl,
                            userId
                    );
                    return ResultData.success(downloadUrl);
                })
                .onErrorResume(e -> Mono.just(ResultData.fail(500, "文档翻译失败: " + e.getMessage())))
                .block();
    }

    private Map<String, Object> buildRequestBody(TranslateRequestDTO dto) {
        return Map.of(
                "sourceLanguage", dto.getSourceLanguage(),
                "targetLanguage", dto.getTargetLanguage(),
                "sourceText", dto.getSourceText(),
                "termbases",dto.isTermbases()
        );
    }
    private Map<String, Object> buildImgRequestBody(ImgTranslDTO imgTranslDTO) {
        return Map.of(
                "sourceLanguage", imgTranslDTO.getSourceLanguage(),
                "targetLanguage", imgTranslDTO.getTargetLanguage(),
                "imgPath", imgTranslDTO.getLocalImgPath()
        );
    }
    private void saveHistory(TranslateRequestDTO dto,
                             String targetText,
                             String reflect,
                             String reflectText,
                             Long userId) {
        History history = new History();
        history.setUserId(userId);
        history.setSourceLang(dto.getSourceLanguage());
        history.setTargetLang(dto.getTargetLanguage());
        history.setSourceText(dto.getSourceText());
        history.setTargetText(targetText);
        history.setReflect(reflect);
        history.setReflectText(reflectText);
        // 异步保存
        Mono.fromRunnable(() -> historyMapper.insertHistory(history))
                .subscribeOn(Schedulers.boundedElastic())
                .doOnError(e -> log.error("历史记录保存失败", e))
                .retry(1) // 失败重试
                .subscribe();
    }
    private void saveImgHistory(ImgTranslDTO dto,
                             String sourceText,
                             String targetText,
                             String reflect,
                             String reflectText,
                             Long userId) {
        ImgHistory imgHistory=new ImgHistory();
        imgHistory.setUserId(userId);
        imgHistory.setSourceLang(dto.getSourceLanguage());
        imgHistory.setTargetLang(dto.getTargetLanguage());
        imgHistory.setSourceText(sourceText);
        imgHistory.setTargetText(targetText);
        imgHistory.setReflect(reflect);
        imgHistory.setReflectText(reflectText);
        imgHistory.setImgPath(dto.getImgPath());
        Mono.fromRunnable(() -> imgHistoryMapper.insertImgHistory(imgHistory))
                .subscribeOn(Schedulers.boundedElastic())
                .doOnError(e -> log.error("历史记录保存失败", e))
                .retry(1) // 失败重试
                .subscribe();
    }
    private void saveDocHistory(String fileName,String filePath,Long userId){
        DocHistory docHistory=new DocHistory();
        docHistory.setFileName(fileName);
        docHistory.setSavePath(filePath);
        docHistory.setUserId(userId);
        Mono.fromRunnable(() -> docHistoryMapper.insert(docHistory))
                .subscribeOn(Schedulers.boundedElastic())  //
                .doOnError(e -> log.error("历史记录保存失败", e))
                .retry(1) // 失败重试
                .subscribe();
    }
    @Override
    public ResultData<String> blueScore(String reference, String candidate){
        return webClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/bleuscore")
                        .queryParam("reference", reference)
                        .queryParam("candidate", candidate)
                        .build())
                .retrieve()
                .bodyToMono(String.class)
                .map(ResultData::success)
                .block();
    }


    @Override
    public ResultData bleuScoreChart(){
        List<Double> firstTransl0=bleuResultMapper.selectFirstScores0();
        List<Double> secondTransl0=bleuResultMapper.selectImproveScores0();
        List<Double> firstTransl1=bleuResultMapper.selectFirstScores1();
        List<Double> secondTransl1=bleuResultMapper.selectImproveScores1();
        return ResultData.success(Map.of(
                "firstTransl0", firstTransl0,
                "secondTransl0", secondTransl0,
                "firstTransl1", firstTransl1,
                "secondTransl1", secondTransl1,
                "AllCount", firstTransl0.size()
        ));
    }

    @Override
    public ResultData refreshChart() {
        try {
            return webClient.get()
                    .uri("/getChart")
                    .retrieve()
                    .bodyToMono(ResultData.class)
                    .block();
        } catch (Exception e) {
            return ResultData.fail(500, "更新错误 " + e.getMessage());
        }
    }
}
