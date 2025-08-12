package com.example.Kcsj.controller;

import com.alibaba.fastjson2.JSONObject;
import com.example.Kcsj.common.Result;
import com.example.Kcsj.entity.ImgRecords;
import com.example.Kcsj.mapper.ImgRecordsMapper;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

import jakarta.annotation.Resource;
import java.util.Date;

@RestController
@RequestMapping("/flask")
public class PredictionController {
    @Resource
    ImgRecordsMapper imgRecordsMapper;

    private final RestTemplate restTemplate = new RestTemplate();

    // 定义接收的参数类
    public static class PredictRequest {
        private String startTime;
        private String weight;
        private String username;
        private String inputImg;
        private String conf;
        private String ai;
        private String suggestion;
        private Boolean thinkMode;

        public String getUsername() {
            return username;
        }

        public void setUsername(String username) {
            this.username = username;
        }

        public String getStartTime() {
            return startTime;
        }

        public void setStartTime(String startTime) {
            this.startTime = startTime;
        }

        public String getWeight() {
            return weight;
        }

        public void setWeight(String weight) {
            this.weight = weight;
        }

        public String getInputImg() {
            return inputImg;
        }

        public void setInputImg(String inputImg) {
            this.inputImg = inputImg;
        }

        public String getConf() {
            return conf;
        }

        public void setConf(String conf) {
            this.conf = conf;
        }

        public String getAi() {
            return ai;
        }

        public void setAi(String ai) {
            this.ai = ai;
        }

        public String getSuggestion() {
            return suggestion;
        }

        public void setSuggestion(String suggestion) {
            this.suggestion = suggestion;
        }

        public Boolean getThinkMode() {
            return thinkMode;
        }

        public void setThinkMode(Boolean thinkMode) {
            this.thinkMode = thinkMode;
        }
    }

    @PostMapping("/predict")
    public Result<?> predict(@RequestBody PredictRequest request) {
        if (request == null || request.getInputImg() == null || request.getInputImg().isEmpty()) {
            return Result.error("-1", "未提供图片链接");
        } else if (request.getWeight() == null || request.getWeight().isEmpty()) {
            return Result.error("-1", "未提供权重");
        }

        try {
            // 创建请求体
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<PredictRequest> requestEntity = new HttpEntity<>(request, headers);

            // 调用 Flask API
            String response = restTemplate.postForObject("http://localhost:5000/predictImg", requestEntity, String.class);
            System.out.println("Received response: " + response);
            JSONObject responses = JSONObject.parseObject(response);
            if(responses.get("status").equals(400)){
                return Result.error("-1", "Error: " + responses.get("message"));
            }else {
                ImgRecords imgRecords = new ImgRecords();
                imgRecords.setWeight(request.getWeight());
                imgRecords.setConf(request.getConf());
                imgRecords.setInputImg(request.getInputImg());
                imgRecords.setUsername(request.getUsername());
                imgRecords.setStartTime(request.getStartTime());
                imgRecords.setAi(request.getAi());
                imgRecords.setLable(String.valueOf(responses.get("label")));
                imgRecords.setConfidence(String.valueOf(responses.get("confidence")));
                imgRecords.setAllTime(String.valueOf(responses.get("allTime")));
                imgRecords.setOutImg(String.valueOf(responses.get("outImg")));
                imgRecords.setSuggestion(String.valueOf(responses.get("suggestion")));
                imgRecordsMapper.insert(imgRecords); // 插入到数据库
                return Result.success(response);
            }
        } catch (Exception e) {
            return Result.error("-1", "Error: " + e.getMessage());
        }
    }

    @GetMapping("/file_names")
    public Result<?> getFileNames() {
        try {
            // 调用 Flask API
            String response = restTemplate.getForObject("http://127.0.0.1:5000/file_names", String.class);
            return Result.success(response);
        } catch (Exception e) {
            return Result.error("-1", "Error: " + e.getMessage());
        }
    }
}
