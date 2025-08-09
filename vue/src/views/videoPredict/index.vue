<template>
	<div class="system-predict-container layout-padding">
		<div class="system-predict-padding layout-padding-auto layout-padding-view">
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
					/>
				</div>
				<div class="conf" style="margin-left: 20px;display: flex; flex-direction: row;">
					<div
						style="font-size: 14px;margin-right: 20px;display: flex;justify-content: start;align-items: center;color: #909399;">
						设置最小置信度阈值</div>
					<el-slider v-model="conf" :format-tooltip="formatTooltip" style="width: 300px;" />
				</div>
				<el-upload v-model="state.form.inputVideo" ref="uploadFile" class="avatar-uploader"
					action="http://localhost:9999/files/upload" :show-file-list="false"
					:on-success="handleAvatarSuccessone">
					<div class="button-section" style="margin-left: 20px">
						<el-button type="info" class="predict-button">上传视频</el-button>
					</div>
				</el-upload>
				<div class="button-section" style="margin-left: 20px">
					<el-button type="primary" @click="upData" class="predict-button">开始处理</el-button>
				</div>
				<div class="demo-progress" v-if="state.isShow">
					<el-progress :text-inside="true" :stroke-width="20" :percentage=state.percentage style="width: 400px;">
						<span>{{ state.type_text }} {{ state.percentage }}%</span>
					</el-progress>
				</div>
			</div>
			
			<!-- 视频检测结果 -->
			<div class="section-title"><i></i><span>检测结果</span></div>
			<div class="result-section">
				<div class="cards" ref="cardsContainer">
					<img v-if="state.video_path" class="video" :src="state.video_path">
					<div v-else class="no-result">尚未有检测结果</div>
				</div>
			</div>
			
			<!-- AI建议部分 -->
			<div class="carousel" v-if="state.video_path">
				<div class="section-title"><i></i><span>AI建议</span></div>
			</div>
			<div style="width: 100%;margin-bottom: 50px;" v-if="state.video_path">
				<div v-if="state.predictionResult.suggestion" style="width:100%;padding: 20px; border-radius: 10px;min-height: 200px;border: 1px solid #ccc; max-height: 600px; overflow-y: auto;">
					<div v-html="state.predictionResult.suggestion" class="markdown-body"></div>
				</div>
				<div v-else-if="state.form.ai && state.form.ai !== '不使用AI'" style="width:100%;padding: 20px; border-radius: 10px;min-height: 50px;border: 1px dashed #ccc; text-align: center; color: #909399;">
					尚未生成AI建议
				</div>
				<div v-else style="width:100%;padding: 20px; border-radius: 10px;min-height: 50px;border: 1px dashed #ccc; text-align: center; color: #909399;">
					未使用AI助手
				</div>
			</div>
		</div>
	</div>
</template>


<script setup lang="ts">
import { reactive, ref, onMounted, onUnmounted } from 'vue';
import { ElMessage } from 'element-plus';
import request from '/@/utils/request';
import { useUserInfo } from '/@/stores/userInfo';
import { storeToRefs } from 'pinia';
import type { UploadInstance, UploadProps } from 'element-plus';
import { SocketService } from '/@/utils/socket';
import { formatDate } from '/@/utils/formatTime';
import { marked } from "marked";

const uploadFile = ref<UploadInstance>();
const stores = useUserInfo();
const conf = ref('');
const weight = ref('');
const ai = ref('');
const thinkMode = ref(false);
const { userInfos } = storeToRefs(stores);

const handleAvatarSuccessone: UploadProps['onSuccess'] = (response, uploadFile) => {
	ElMessage.success('上传成功！');
	state.form.inputVideo = response.data;
};
const state = reactive({
	loading: false,
	weight_items: [] as any,
	video_path: '',
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
			label: '使用qwen2.5-VL（局域网）',
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
			label: '使用qwen3.0（本地）',
		},
		{
			value: 'Qwen2.5-VL-Local',
			label: '使用qwen2.5-VL（本地）',
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
		inputVideo: null as any,
		weight: '',
		conf: null as any,
		ai: '',
		thinkMode: '' as string,
		startTime: ''
	},
	type_text: "正在保存",
	percentage: 50,
	isShow: false,
});

const socketService = new SocketService();

// 确保只初始化一次Socket连接
let socketInitialized = false;

const initSocket = () => {
	if (!socketInitialized) {
		console.log('初始化Socket连接...');
		
		socketService.on('message', (data) => {
			console.log('Received message:', data);
			ElMessage.success(data);
		});

		socketService.on('progress', (data) => {
			state.percentage = parseInt(data);
			if (parseInt(data) < 100) {
				state.isShow = true;
			} else {
				//两秒后隐藏进度条
				ElMessage.success("保存成功！");
				setTimeout(() => {
					state.isShow = false;
					state.percentage = 0;
				}, 2000);
			}
			console.log('Received progress:', data);
		});

		socketService.on('suggestion', (data) => {
			console.log('Received suggestion:', data);
			try {
				state.predictionResult.suggestion = marked(data);
				console.log('After marking suggestion:', state.predictionResult.suggestion);
				ElMessage.success("AI建议生成成功！");
			} catch (error) {
				console.error('处理建议时出错:', error);
				state.predictionResult.suggestion = data;
			}
		});
		
		socketInitialized = true;
	}
};

const formatTooltip = (val: number) => {
	return val / 100
}

const getData = () => {
	request.get('/api/flask/file_names').then((res) => {
		if (res.code == 0) {
			res.data = JSON.parse(res.data);
			console.log(res.data);
			state.weight_items = res.data.weight_items;
		} else {
			ElMessage.error(res.msg);
		}
	});
};


const upData = () => {
	if (!state.form.inputVideo) {
		ElMessage.error('请先上传视频文件！');
		return;
	}
	if (!weight.value) {
		ElMessage.error('请选择检测模型！');
		return;
	}
	if (!ai.value) {
		ElMessage.error('请选择AI助手！');
		return;
	}
	
	// 确保Socket连接已初始化
	initSocket();
	
	state.loading = true;
	state.form.weight = weight.value;
	state.form.conf = (parseFloat(conf.value) / 100);
	state.form.username = userInfos.value.userName;
	state.form.ai = ai.value;
	state.form.thinkMode = thinkMode.value ? "true" : "false";
	state.form.startTime = formatDate(new Date(), 'YYYY-mm-dd HH:MM:SS');
	console.log('提交请求，思考模式状态:', thinkMode.value, '表单中的值:', state.form.thinkMode);
	console.log(state.form);
	const queryParams = new URLSearchParams();
	Object.keys(state.form).forEach(key => {
		if (state.form[key] !== null && state.form[key] !== undefined) {
			queryParams.append(key, state.form[key]);
		}
	});
	state.video_path = `http://127.0.0.1:5000/predictVideo?${queryParams.toString()}`;
	ElMessage.success('正在加载！');
	
	// 清空之前的AI建议
	state.predictionResult.suggestion = '';
};

onMounted(() => {
	getData();
	initSocket();
});

onUnmounted(() => {
	// 组件销毁时断开Socket连接
	socketService.disconnect();
	socketInitialized = false;
});
</script>

<style scoped lang="scss">
.predict-button {
	background: #9E87FF;
	width: 100%;
	/* 按钮宽度填满 */
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

.result-section {
	margin-top: 15px;
	margin-bottom: 30px;
	display: flex;
	justify-content: center;
	align-items: center;
	min-height: 400px;
}

.cards {
	width: 100%;
	border-radius: 5px;
	padding: 20px;
	overflow: hidden;
	display: flex;
	justify-content: center;
	align-items: center;
	/* 防止视频溢出 */
	max-height: 600px;
}

.no-result {
	width: 100%;
	height: 300px;
	display: flex;
	justify-content: center;
	align-items: center;
	border: 1px dashed #ccc;
	color: #909399;
}

.video {
	max-width: 80%;
	max-height: 600px;
	height: auto;
	width: auto;
	object-fit: contain;
	margin: 0 auto;
	display: block;
}

.button-section {
	display: flex;
	justify-content: center;
}

.predict-button {
	width: 100%;
	/* 按钮宽度填满 */
}

.demo-progress .el-progress--line {
	margin-left: 20px;
	width: 600px;
}

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

.section-title {
	margin-bottom: 20px;
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

.markdown-body {
	line-height: 1.6;
	font-size: 16px;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
	margin-top: 24px;
	margin-bottom: 16px;
	font-weight: 600;
	line-height: 1.25;
}

.markdown-body h1 {
	font-size: 2em;
	padding-bottom: 0.3em;
	border-bottom: 1px solid #eaecef;
}

.markdown-body h2 {
	font-size: 1.5em;
	padding-bottom: 0.3em;
	border-bottom: 1px solid #eaecef;
}

.markdown-body h3 {
	font-size: 1.25em;
}

.markdown-body p,
.markdown-body ul,
.markdown-body ol {
	margin-top: 0;
	margin-bottom: 16px;
}

.markdown-body ul,
.markdown-body ol {
	padding-left: 2em;
}

.markdown-body li + li {
	margin-top: 0.25em;
}

.markdown-body pre {
	background: #f6f8fa;
	padding: 16px;
	border-radius: 5px;
	overflow-x: auto;
	margin-bottom: 16px;
}

.markdown-body code {
	background: #f6f8fa;
	padding: 3px 6px;
	border-radius: 3px;
	font-family: monospace;
}

.markdown-body blockquote {
	padding: 0 1em;
	color: #6a737d;
	border-left: 0.25em solid #dfe2e5;
	margin: 0 0 16px 0;
}

.markdown-body table {
	border-collapse: collapse;
	width: 100%;
	margin-bottom: 16px;
}

.markdown-body table th,
.markdown-body table td {
	padding: 6px 13px;
	border: 1px solid #dfe2e5;
}

.markdown-body table tr {
	background-color: #fff;
	border-top: 1px solid #c6cbd1;
}

.markdown-body table tr:nth-child(2n) {
	background-color: #f6f8fa;
}
</style>