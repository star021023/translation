package com.example.translation.mapper;

import com.example.translation.pojo.po.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;
import org.springframework.data.repository.query.Param;
@Mapper
public interface AdminMapper {
    @Select("SELECT COUNT(*) FROM admin WHERE username = #{username} AND password = #{password}")
    int checkAdminCredentials(@Param("username") String username, @Param("password") String password);
    @Select("SELECT * FROM admin WHERE username = #{username}")
    User findAdminByUsername(@Param("username") String username);

    @Update(" UPDATE admin SET name = #{newName} WHERE id = #{userId}")
    void updateAdminName(Long userId,String newName);
    @Update(" UPDATE admin SET avatar = #{avatar} WHERE id = #{userId}")
    void updateAvatar(Long userId,String avatar);
    @Select(" SELECT * FROM admin WHERE id = #{userId}")
    User findAdminById(Long userId);
    @Select("SELECT COUNT(*) FROM admin WHERE name = #{name}")
    Integer checkNameExists(String name);
}
