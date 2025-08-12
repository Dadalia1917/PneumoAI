package com.example.Kcsj.controller;

import cn.hutool.core.util.StrUtil;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.Kcsj.common.Result;
import com.example.Kcsj.entity.ImgRecords;
import com.example.Kcsj.mapper.ImgRecordsMapper;
import org.springframework.web.bind.annotation.*;

import jakarta.annotation.Resource;

@RestController
@RequestMapping("/imgRecords")
public class ImgRecordsController {
    @Resource
    ImgRecordsMapper imgRecordsMapper;

    @GetMapping("/all")
    public Result<?> GetAll() {
        return Result.success(imgRecordsMapper.selectList(null));
    }
    @GetMapping("/{id}")
    public Result<?> getById(@PathVariable int id) {
        System.out.println(id);
        return Result.success(imgRecordsMapper.selectById(id));
    }

    @GetMapping
    public Result<?> findPage(@RequestParam(value = "pageNum", defaultValue = "1") Integer pageNum,
                              @RequestParam(value = "pageSize", defaultValue = "10") Integer pageSize,
                              @RequestParam(value = "search", defaultValue = "") String search,
                              @RequestParam(value = "search1", defaultValue = "") String search1,
                              @RequestParam(value = "search3", defaultValue = "") String search3,
                              @RequestParam(value = "search2", defaultValue = "") String search2) {
        LambdaQueryWrapper<ImgRecords> wrapper = Wrappers.<ImgRecords>lambdaQuery();
        wrapper.orderByDesc(ImgRecords::getStartTime);
        if (StrUtil.isNotBlank(search)) {
            wrapper.like(ImgRecords::getUsername, search);
        }
        if (StrUtil.isNotBlank(search1)) {
            wrapper.like(ImgRecords::getStartTime, search1);
        }
        if (StrUtil.isNotBlank(search2)) {
            wrapper.like(ImgRecords::getLable, search2);
        }
        if (StrUtil.isNotBlank(search3)) {
            wrapper.like(ImgRecords::getConf, search3);
        }
        Page<ImgRecords> Page = imgRecordsMapper.selectPage(new Page<>(pageNum, pageSize), wrapper);
        return Result.success(Page);
    }

    @DeleteMapping("/{id}")
    public Result<?> delete(@PathVariable int id) {
        imgRecordsMapper.deleteById(id);
        return Result.success();
    }

    @PostMapping("/update")
    public Result<?> updates(@RequestBody ImgRecords imgrecords) {
        imgRecordsMapper.updateById(imgrecords);
        return Result.success();
    }


    @PostMapping
    public Result<?> save(@RequestBody ImgRecords imgrecords) {
        System.out.println(imgrecords);
        imgRecordsMapper.insert(imgrecords);
        return Result.success();
    }
}
