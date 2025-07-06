package com.example.translation.controller;

import com.example.translation.pojo.po.DocHistory;
import com.example.translation.pojo.po.History;
import com.example.translation.pojo.vo.HistoryVO;
import com.example.translation.pojo.vo.ImgHistoryVO;
import com.example.translation.service.HistoryService;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/history")
public class HistoryController {
    @Autowired
    private HistoryService historyService;

    // 插入一条历史记录
    @PostMapping
    public int insertHistory(@RequestBody History history) {
        return historyService.insertHistory(history);
    }

    // 根据 ID 删除一条历史记录
    @DeleteMapping("/delete/{id}")
    public int deleteHistoryById(@PathVariable Long id, HttpServletRequest request) {
        return historyService.deleteHistoryById(id,request);
    }
    @PutMapping
    public int updateHistory(@RequestBody History history) {
        return historyService.updateHistory(history);
    }
    @GetMapping("/search")
    public List<HistoryVO>  searchHistories(@RequestParam String text,HttpServletRequest request) {
        return historyService.searchHistories(text,request);
    }
    @GetMapping("/getAll")
    public List<HistoryVO>  selectAllHistories(HttpServletRequest request) {
        return historyService.selectAllHistories(request);
    }

    @GetMapping("/getImgHistory")
    public List<ImgHistoryVO> selectAllImgHistory(){
        return historyService.selectAllImgHistory();
    }

    @DeleteMapping("/imgDelete/{id}")
    public int deleteImgHistory(@PathVariable Long id){
        return historyService.deleteImgHistory(id);
    }

    @PostMapping("/searchImgHistory")
    public List<ImgHistoryVO> searchImgHistory(@RequestParam String text){
        return historyService.searchImgHistories(text);
    }
    @GetMapping("/selectDocHistory")
    public List<DocHistory> selectDocHistory(){
        return historyService.selectDocHistories();
    }
    @DeleteMapping("docDelete/{id}")
    public int deleteDocHistory(@PathVariable Long id){
        return historyService.deleteDocHistory(id);
    }
}
