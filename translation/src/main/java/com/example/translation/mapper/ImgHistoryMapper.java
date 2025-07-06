package com.example.translation.mapper;

import com.example.translation.pojo.po.ImgHistory;
import com.example.translation.pojo.vo.ImgHistoryVO;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface ImgHistoryMapper {
    @Insert("INSERT INTO imghistory(userId, sourceLang, targetLang, sourceText, targetText, reflect, reflectText, imgPath) " +
            "VALUES(#{userId}, #{sourceLang}, #{targetLang}, #{sourceText}, #{targetText}, #{reflect}, #{reflectText}, #{imgPath})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insertImgHistory(ImgHistory imghistory);
    @Delete("DELETE FROM imghistory WHERE id = #{id} and userId=#{userId}")
    int deleteImgHistory(long id,long userId);

    @Select("SELECT * FROM imghistory WHERE userId = #{userId}")
    List<ImgHistoryVO> selectImgHistory(long userId);

    @Select("SELECT * FROM imghistory WHERE userId = #{userId} AND (targetText LIKE CONCAT('%', #{text}, '%') OR sourceText LIKE CONCAT('%', #{text}, '%')")
    List<ImgHistoryVO> searchImgHistories(Long userId,String text);
}
