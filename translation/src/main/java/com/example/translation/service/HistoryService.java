package com.example.translation.service;

import com.example.translation.pojo.po.DocHistory;
import com.example.translation.pojo.po.History;
import com.example.translation.pojo.po.ImgHistory;
import com.example.translation.pojo.vo.HistoryVO;
import com.example.translation.pojo.vo.ImgHistoryVO;
import jakarta.servlet.http.HttpServletRequest;

import java.util.List;

public interface HistoryService {

    int insertHistory(History history);



    int deleteHistoryById(Long id, HttpServletRequest request);

    int updateHistory(History history);


    List<HistoryVO> searchHistories(String keyword, HttpServletRequest request);

    List<HistoryVO> selectAllHistories(HttpServletRequest request);

    List<ImgHistoryVO> selectAllImgHistory();

    int deleteImgHistory(Long id);

    int insertImgHistory(ImgHistory imgHistory);
    List<ImgHistoryVO> searchImgHistories(String text);

    List<DocHistory> selectDocHistories();

    int insertDocHistory(DocHistory docHistory);

    int deleteDocHistory(Long id);
}
