package com.example.translation.mapper;

import com.example.translation.pojo.po.User;
import org.apache.ibatis.annotations.Mapper;
@Mapper
public interface UserMapper {
    void insertUser(User user);
    Integer checkUsernameOrPasswordExists(String username, String password);
    Integer checkUsernameAndPasswordExists(String username, String password);
    Integer checkNameExists(String name);
    User findUserInfoByUsernameAndPassword(String username,String password);
}