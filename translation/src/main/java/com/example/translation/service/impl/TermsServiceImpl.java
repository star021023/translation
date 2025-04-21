package com.example.translation.service.impl;

import com.example.translation.common.result.ResultData;
import com.example.translation.common.result.ReturnCode;
import com.example.translation.mapper.TermsMapper;
import com.example.translation.pojo.po.ParallelCorpus;
import com.example.translation.pojo.po.Terms;
import com.example.translation.service.TermsService;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.ss.usermodel.WorkbookFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.ArrayList;
import java.util.List;

@Service
public class TermsServiceImpl implements TermsService {
    @Autowired
    private TermsMapper termsMapper;
    @Override
    public List<Terms> selectAllTerms(){
        return termsMapper.selectAllTerms();
    }

    @Override
    public List<Terms> selectByKeywords(String keywords){
        return termsMapper.selectByKeywords(keywords);
    }

    @Override
    public int deleteById(int id){
        return termsMapper.deleteById(id);
    }

    @Override
    public int updateTerms(Terms terms){
        return termsMapper.updateTerms(terms);
    }

    @Override
    public int insertTerms(Terms terms){
        return termsMapper.insertTerms(terms);
    }

    @Override
    public List<ParallelCorpus> selectAllParallelCorpus(){
        return termsMapper.selectAllParallelCorpus();
    }
    @Override
    public List<ParallelCorpus> searchParallelCorpus(String keywords){
        return termsMapper.searchParallelCorpus(keywords);
    }
    @Override
    public int deleteParallelCorpus(int id){
        return termsMapper.deleteParallelCorpus(id);
    }
    @Override
    public int updateParallelCorpus(ParallelCorpus parallelCorpus){
        return termsMapper.updateParallelCorpus(parallelCorpus);
    }
    @Override
    public int insertParallelCorpus(ParallelCorpus parallelCorpus){
        return termsMapper.insertParallelCorpus(parallelCorpus);
    }

    @Override
    public ResultData importParallelCorpus(MultipartFile file) {
        try {
            Workbook workbook = WorkbookFactory.create(file.getInputStream());
            Sheet sheet = workbook.getSheetAt(0); // 获取第一个工作表
            List<ParallelCorpus> parallelCorpusList = new ArrayList<>();
            // 跳过表头行
            for (int i = 1; i <= sheet.getLastRowNum(); i++) {
                Row row = sheet.getRow(i);
                if (row == null) continue;
                ParallelCorpus parallelCorpus=new ParallelCorpus();
                parallelCorpus.setChinese(row.getCell(0).getStringCellValue());
                parallelCorpus.setEnglish(row.getCell(1).getStringCellValue());
                parallelCorpusList.add(parallelCorpus);
            }
            if (!parallelCorpusList.isEmpty()) {
                termsMapper.batchInsertParallelCorpus(parallelCorpusList); // 需要实现批量插入方法
            }
            return ResultData.success("成功导入" + sheet.getLastRowNum() + "条数据");
        } catch (Exception e) {
            return ResultData.fail(ReturnCode.RC999.getCode(), "导入失败: " + e.getMessage());
        }
    }
}
