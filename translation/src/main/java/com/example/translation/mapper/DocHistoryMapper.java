package com.example.translation.mapper;

import com.example.translation.pojo.po.DocHistory;
import org.apache.ibatis.annotations.*;

import java.util.List;

@Mapper
public interface DocHistoryMapper {
    @Insert("INSERT INTO dochistory(userId, savePath, fileName) " +
            "VALUES(#{userId}, #{savePath}, #{fileName})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(DocHistory docHistory);

    @Delete("DELETE FROM dochistory WHERE id = #{id} AND userId = #{userId}")
    int deleteById( long id, long userId);

    @Select("SELECT * FROM dochistory WHERE userId = #{userId}")
    List<DocHistory> selectDocHistory(long userId);
}
