package com.example.Kcsj.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@TableName("camerarecords")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class CameraRecords {
    @TableId(type = IdType.AUTO)
    private Integer id;
    private String weight;
    private String inputVideo;
    private String outVideo;
    private String confidence;
    private String allTime;
    private String conf;
    private String label;
    private String username;
    private String startTime;
    private String ai;

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

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

    public String getInputVideo() {
        return inputVideo;
    }

    public void setInputVideo(String inputVideo) {
        this.inputVideo = inputVideo;
    }

    public String getOutVideo() {
        return outVideo;
    }

    public void setOutVideo(String outVideo) {
        this.outVideo = outVideo;
    }

    public String getConfidence() {
        return confidence;
    }

    public void setConfidence(String confidence) {
        this.confidence = confidence;
    }

    public String getAllTime() {
        return allTime;
    }

    public void setAllTime(String allTime) {
        this.allTime = allTime;
    }

    public String getConf() {
        return conf;
    }

    public void setConf(String conf) {
        this.conf = conf;
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }

    public String getAi() {
        return ai;
    }

    public void setAi(String ai) {
        this.ai = ai;
    }
}
