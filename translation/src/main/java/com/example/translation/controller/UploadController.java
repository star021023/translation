package com.example.translation.controller;

import com.example.translation.common.result.ResultData;
import com.example.translation.common.result.ReturnCode;
import com.example.translation.pojo.dto.DataChunk;
import com.example.translation.pojo.vo.UserVO;
import com.example.translation.service.UploadFile;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Flux;

@RestController
@RequestMapping("/upload")
public class UploadController {
    @Autowired
    private UploadFile uploadFile;

    @PostMapping(value = "/avatar" , consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResultData<UserVO> uploadOssFile(@RequestParam("file") @RequestBody MultipartFile file){
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null ||
                !originalFilename.matches(".*\\.(jpg|jpeg|png|gif|bmp)$")) {
            return ResultData.fail(ReturnCode.RC999.getCode(), "仅支持jpg/jpeg/png/gif/bmp格式图片");
        }
        return uploadFile.uploadFileAvatar(file);
    }

    @PostMapping(value = "/admin/avatar" , consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResultData<UserVO> uploadAdminFile(@RequestParam("file") @RequestBody MultipartFile file){
        String originalFilename = file.getOriginalFilename();
        if (originalFilename == null ||
                !originalFilename.matches(".*\\.(jpg|jpeg|png|gif|bmp)$")) {
            return ResultData.fail(ReturnCode.RC999.getCode(), "仅支持jpg/jpeg/png/gif/bmp格式图片");
        }
        return uploadFile.uploadAdminAvatar(file);
    }


    @PostMapping(value = "/image", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Flux<ServerSentEvent<ResultData<DataChunk>>> uploadImage(@RequestParam("sourceLanguage") String sourceLanguage,
                                                        @RequestParam("targetLanguage") String targetLanguage,
                                                        @RequestParam("file") MultipartFile file) {
        return uploadFile.imgUpload(sourceLanguage,targetLanguage,file).map(sse -> {
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

    @PostMapping(value = "/word", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResultData<String> uploadWord(@RequestParam("sourceLanguage") String sourceLanguage,
                                 @RequestParam("targetLanguage") String targetLanguage,
                                 @RequestParam("file") MultipartFile file){
        return uploadFile.uploadWord(sourceLanguage,targetLanguage,file);
    }

}
