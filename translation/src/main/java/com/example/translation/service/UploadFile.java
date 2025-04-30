package com.example.translation.service;

import com.example.translation.common.result.ResultData;
import com.example.translation.pojo.dto.DataChunk;
import com.example.translation.pojo.vo.UserVO;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.web.multipart.MultipartFile;
import reactor.core.publisher.Flux;

public interface UploadFile {

    ResultData<UserVO> uploadFileAvatar(MultipartFile multipartFile);

    ResultData<UserVO> uploadAdminAvatar(MultipartFile multipartFile);

    Flux<ServerSentEvent<DataChunk>> imgUpload(String sourceLanguage, String targetLanguage, MultipartFile multipartFile);


    ResultData<String> uploadWord(String sourceLanguage, String targetLanguage, MultipartFile multipartFile);
}
