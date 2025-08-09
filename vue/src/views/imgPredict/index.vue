<template>
	<div class="system-predict-container layout-padding" id="id" v-loading="state.loading">
		<div class="system-predict-padding layout-padding-auto layout-padding-view">
			<div class="carousel">
				<div class="section-title"><i></i><span>肺炎检测</span></div>
			</div>
			<div class="header">
				<div class="weight">
					<el-select v-model="weight" placeholder="请选择模型" size="large" style="width: 200px">
						<el-option v-for="item in state.weight_items" :key="item.value" :label="item.label"
							:value="item.value" />
					</el-select>
				</div>
				<div class="weight">
					<el-select v-model="ai" placeholder="请选择AI助手" size="large" style="margin-left: 20px;width: 200px"
						@change="getData">
						<el-option v-for="item in state.ai_items" :key="item.value" :label="item.label"
							:value="item.value" />
					</el-select>
				</div>
				<div v-if="ai && (ai === 'Qwen3.0-Local' || ai === 'Qwen3.0-LAN')" style="margin-left: 20px;">
					<el-switch
						v-model="thinkMode"
						active-text="思考模式"
						inactive-text="非思考模式"
						style="margin-top: 5px;"
						@change="(val) => { console.log('思考模式切换:', val) }"
					/>
				</div>
				<div class="conf" style="margin-left: 20px;display: flex; flex-direction: row;">
					<div
						style="font-size: 14px;margin-right: 20px;display: flex;justify-content: start;align-items: center;color: #909399;">
						设置最小置信度阈值</div>
					<el-slider v-model="conf" :format-tooltip="formatTooltip" style="width: 300px;" />
				</div>
				<div class="button-section" style="margin-left: 20px">
					<el-button type="primary" @click="upData" class="predict-button">开始检测</el-button>
				</div>
				<div class="button-section" style="margin-left: 20px">
					<el-button type="primary" @click="() => htmlToPDF('id', '肺炎检测报告')"
						class="predict-button">PDF导出</el-button>
				</div>
			</div>
			<div style="width: 100%; height: 800px; display: flex; flex-direction: row;margin-bottom: 20px;">
				<el-card shadow="hover" class="card">
					<el-upload v-model="state.img" ref="uploadFile" class="avatar-uploader"
						action="http://localhost:9999/files/upload" :show-file-list="false"
						:on-success="handleAvatarSuccessone">
						<img v-if="imageUrl" :src="imageUrl" class="avatar" />
						<el-icon v-else class="avatar-uploader-icon">
							<Plus />
						</el-icon>
					</el-upload>
				</el-card>
				<el-card class="result-section" v-if="state.predictionResult.label">
					<div class="bottom">
						<div class="result-content">
							<el-card shadow="never" class="info-card">
								<div class="info-item">
									<div class="info-label">
										<el-icon class="icon"><Select /></el-icon>
										<span>识别结果</span>
									</div>
									<div class="info-value highlight">{{ state.predictionResult.label || '-' }}
									</div>
								</div>

								<div class="info-item">
									<div class="info-label">
										<el-icon class="icon">
											<Opportunity />
										</el-icon>
										<span>检测概率</span>
									</div>
									<div class="info-value accent">
										{{ state.predictionResult.confidence || '-' }}
									</div>
								</div>

								<div class="info-item">
									<div class="info-label">
										<el-icon class="icon">
											<Clock />
										</el-icon>
										<span>总耗时</span>
									</div>
									<div class="info-value">{{ state.predictionResult.allTime ?
										`${state.predictionResult.allTime}` : '-' }}</div>
								</div>
							</el-card>
						</div>
						<div style="width: 100%; margin-top: 20px;">
							<h4>详细结果</h4>
							<el-table :data="state.data" style="width: 100%">
								<el-table-column prop="label" label="检测结果" align="center" />
								<el-table-column prop="confidence" label="置信度" align="center" />
								<el-table-column prop="allTime" label="总用时" align="center" />
							</el-table>
						</div>
					</div>
				</el-card>
			</div>
			<div class="carousel">
				<div class="section-title"><i></i><span>AI建议</span></div>
			</div>
			<div style="width: 100%;margin-bottom: 20px; padding: 0 300px;">
				<div v-if="state.predictionResult.suggestion" style="width:100%;padding: 20px 100px; border-radius: 10px;min-height: 50px;border: 1px solid #ccc">
					<div v-html="state.predictionResult.suggestion" class="markdown-body"></div>
				</div>
			</div>
		</div>
	</div>
</template>


<script setup lang="ts" name="personal">
import { reactive, ref, onMounted } from 'vue';
import type { UploadInstance, UploadProps } from 'element-plus';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { Loading, Plus } from '@element-plus/icons-vue';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import { formatDate } from '/@/utils/formatTime';
import { htmlToPDF } from '/@/utils/pdf'
import { marked } from "marked";
import { SocketService } from '/@/utils/socket';

const imageUrl = ref('');
const ai = ref('');
const conf = ref('');
const weight = ref('');
const thinkMode = ref(false);
const uploadFile = ref<UploadInstance>();
const stores = useUserInfo();
const { userInfos } = storeToRefs(stores);
const state = reactive({
	loading: false,
	weight_items: [] as any,
	img: '',
	data: [] as any,
	predictionResult: {
		label: '',
		confidence: '',
		allTime: '',
		suggestion: '' as any
	},
	ai_items: [
		{
			value: 'Deepseek-R1',
			label: '使用Deepseek-R1',
		},
		{
			value: 'Qwen',
			label: '使用Qwen',
		},
		{
			value: 'Deepseek-R1-LAN',
			label: '使用Deepseek-R1（局域网）',
		},
		{
			value: 'Qwen3.0-LAN',
			label: '使用qwen3.0（局域网）',
		},
		{
			value: 'Qwen2.5-VL-LAN',
			label: '使用Qwen2.5-VL（局域网）',
		},
		{
			value: 'Qwen2.5-Omni-LAN',
			label: '使用Qwen2.5-Omni（局域网）',
		},
		{
			value: 'Gemma3-LAN',
			label: '使用Gemma3（局域网）',
		},
		{
			value: 'Deepseek-R1-Local',
			label: '使用Deepseek-R1（本地）',
		},
		{
			value: 'Qwen3.0-Local',
			label: '使用Qwen3.0（本地）',
		},
		{
			value: 'Qwen2.5-VL-Local',
			label: '使用Qwen2.5-VL（本地）',
		},
		{
			value: 'Qwen2.5-Omni-Local',
			label: '使用Qwen2.5-Omni（本地）',
		},
		{
			value: 'Gemma3-Local',
			label: '使用Gemma3（本地）',
		},
		{
			value: '不使用AI',
			label: '不使用大模型',
		},
	],
	form: {
		username: '',
		inputImg: null as any,
		weight: '',
		conf: null as any,
		ai: '',
		thinkMode: false as boolean,
		startTime: ''
	},
});

const formatTooltip = (val: number) => {
	return val / 100
}
const socketService = new SocketService();

socketService.on('message', (data) => {
	console.log('Received message:', data);
	ElMessage({
    message: data,
    type: 'success',
	duration: 3000
  })
});

const handleAvatarSuccessone: UploadProps['onSuccess'] = (response, uploadFile) => {
	imageUrl.value = URL.createObjectURL(uploadFile.raw!);
	state.img = response.data;
};

const getData = () => {
	request.get('/api/flask/file_names').then((res) => {
		if (res.code == 0) {
			res.data = JSON.parse(res.data);
			state.weight_items = res.data.weight_items;
		} else {
			ElMessage.error(res.msg);
		}
	});
};
const transformData = (rawData: any): any => {
	return rawData.label.map((label, index) => ({
		allTime: rawData.allTime,
		confidence: rawData.confidence[index],
		label: label,
	}));
}

const upData = () => {
	state.loading = true;
	state.form.weight = weight.value;
	state.form.conf = (parseFloat(conf.value) / 100);
	state.form.username = userInfos.value.userName;
	state.form.inputImg = state.img;
	state.form.ai = ai.value;
	
	// 强制确保thinkMode是布尔值
	if (ai.value === 'Qwen3.0-Local' || ai.value === 'Qwen3.0-LAN' || 
	    ai.value === 'Qwen2.5-VL-Local' || ai.value === 'Qwen2.5-VL-LAN') {
		state.form.thinkMode = thinkMode.value === true;
	} else {
		state.form.thinkMode = false;
	}
	
	console.log('提交请求，思考模式状态:', thinkMode.value, '类型:', typeof thinkMode.value, '表单中的值:', state.form.thinkMode);
	state.form.startTime = formatDate(new Date(), 'YYYY-mm-dd HH:MM:SS');
	
	const requestData = {
		...state.form,
		thinkMode: state.form.thinkMode
	};
	console.log('最终提交数据:', requestData);
	
	request.post('/api/flask/predict', requestData).then((res) => {
		if (res.code == 0) {
			try {
				state.loading = false;
				res.data = JSON.parse(res.data);
				state.predictionResult.label = JSON.parse(res.data.label);
				state.predictionResult.confidence = JSON.parse(res.data.confidence);
				state.predictionResult.allTime = res.data.allTime;
				state.predictionResult.suggestion = marked(res.data.suggestion);
				state.data = transformData(state.predictionResult);

				// 使用处理后的图片替换原图
				if (res.data.outImg) {
					imageUrl.value = res.data.outImg;
				}
			} catch (error) {
				console.error('解析 JSON 时出错:', error);
			}
			ElMessage.success('检测成功！');
		} else {
			state.loading = false;
			ElMessage.error(res.msg);
		}
	});
};

const testThinkMode = () => {
	console.log('测试思考模式:', thinkMode.value);
	
	// 直接发送原始布尔值
	request.post('/api/flask/test_think_mode', {
		thinkMode: thinkMode.value
	}).then((res) => {
		console.log('测试结果:', res);
		ElMessage.success(`服务器接收到的值: ${res.received}`);
	});
	
	// 以字符串形式发送
	request.post('/api/flask/test_think_mode', {
		thinkMode: thinkMode.value ? "true" : "false"
	}).then((res) => {
		console.log('字符串测试结果:', res);
		ElMessage.success(`服务器接收到的字符串值: ${res.received}`);
	});
	
	// 尝试直接使用Fetch API绕过请求库
	fetch('http://localhost:5000/test_think_mode', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({ thinkMode: thinkMode.value })
	})
	.then(response => response.json())
	.then(data => {
		console.log('Fetch API测试结果:', data);
		ElMessage.success(`直接Fetch API结果: ${data.received}`);
	})
	.catch(error => {
		console.error('Fetch错误:', error);
		ElMessage.error('Fetch API请求失败');
	});
};

onMounted(() => {
	getData();
});
</script>

<style scoped lang="scss">
.carousel {
	width: 100%;

	.section-title {
		margin-bottom: 50px;
		font-size: 20px;
		text-align: center;
		position: relative;
		padding: 20px 0;
		display: flex;
		justify-content: center;
		justify-items: center;

		i {
			background: #9E87FF;
			height: 1px;
			width: 100%;
			position: absolute;
			top: 40px;
		}

		span {
			background: #9E87FF;
			line-height: 40px;
			position: absolute;
			width: 120px;
			left: 50%;
			margin-left: -60px;
			color: #fff;
		}
	}
}

.markdown-body {
	line-height: 1.6;
	font-size: 16px;
}

.markdown-body pre {
	background: #f4f4f4;
	padding: 10px;
	border-radius: 5px;
	overflow-x: auto;
}

.markdown-body code {
	background: #f4f4f4;
	padding: 2px 5px;
	border-radius: 3px;
}

.system-predict-container {
	width: 100%;
	height: 100%;
	display: flex;
	flex-direction: column;
	overflow: auto;


	.system-predict-padding {
		padding: 0 100px;
		overflow-y: auto;

		.el-table {
			flex: 1;
		}
	}
}

.header {
	width: 100%;
	height: 5%;
	display: flex;
	justify-content: start;
	align-items: center;
	font-size: 20px;
}

.card {
	width: 100%;
	height: 100%;
	border-radius: 10px;
	margin-top: 15px;
	display: flex;
	justify-content: center;
	align-items: center;
}

.avatar-uploader .avatar {
	width: 100%;
	height: 600px;
	display: block;
}

.el-icon.avatar-uploader-icon {
	font-size: 28px;
	color: #8c939d;
	width: 100%;
	height: 600px;
	text-align: center;
}


.button-section {
	display: flex;
	justify-content: center;
}

.predict-button {
	background: #9E87FF;
	width: 100%;
	/* 按钮宽度填满 */
}

.result-section {
	width: 100%;
	display: flex;
	/* 添加 display: flex; */
	flex-direction: column;
	border-radius: 6px;
}

.bottom {
	width: 100%;
	font-size: 18px;
	display: flex;
	/* 添加 display: flex; */
	flex-direction: row;
	justify-content: center;
	align-items: center;
}

.result-section {
	width: 50%;
	height: 100%;
	margin-top: 15px;
	margin-left: 15px;
	text-align: center;
	display: flex;
	/* 添加 display: flex; */
	flex-direction: column;
	border-radius: 6px;
}

.bottom {
	width: 100%;
	font-size: 18px;
	display: flex;
	/* 添加 display: flex; */
	flex-direction: column;
	justify-content: center;
	align-items: center;
}

.result-content {
	width: 100%;
	margin-top: 16px;

	.info-card {
		padding: 20px;
		border-radius: 8px;
		background: #f8f9fa;
		box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.06);
	}

	.info-item {
		margin: 12px 0;
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		/* 调整为顶部对齐 */
		padding: 8px 0;
		border-bottom: 1px solid #eee;

		&:last-child {
			border-bottom: none;
		}

		.info-label {
			display: flex;
			align-items: center;
			color: #606266;
			font-size: 14px;

			.icon {
				margin-right: 8px;
				font-size: 16px;
				color: #409eff;
			}
		}

		.info-value {
			font-size: 16px;
			font-weight: 500;
			color: #303133;
			flex: 1;
			/* 让内容部分占据剩余空间 */
			margin-left: 16px;
			/* 增加左边距，避免与标签紧贴 */

			&.highlight {
				color: #67c23a;
				font-weight: 600;
			}

			&.accent {
				color: #e6a23c;
			}

			/* 滚动条样式 */
			&::-webkit-scrollbar {
				width: 6px;
			}

			&::-webkit-scrollbar-thumb {
				background: #c1c1c1;
				border-radius: 4px;
			}

			&::-webkit-scrollbar-track {
				background: #f1f1f1;
				border-radius: 4px;
			}
		}
	}
}
</style>
