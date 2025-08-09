<template>
	<div class="home-container layout-pd">
		<el-row :gutter="15" class="home-card-two mb15">
			<el-col :xs="24" :sm="14" :md="14" :lg="16" :xl="16">
				<div class="home-card-item">
					<div style="height: 100%" ref="homeBarRef"></div>
				</div>
			</el-col>
			<el-col :xs="24" :sm="10" :md="10" :lg="8" :xl="8" class="home-media">
				<div class="home-card-item">
					<div style="height: 100%" ref="homePieRef"></div>
				</div>
			</el-col>
		</el-row>
		<el-row :gutter="15" class="home-card-three">
			<el-col :xs="24" :sm="14" :md="14" :lg="8" :xl="8" class="home-media">
				<div class="home-card-item">
					<div style="height: 100%" ref="homeradarRef"></div>
				</div>
			</el-col>
			<el-col :xs="24" :sm="10" :md="10" :lg="16" :xl="16">
				<div class="home-card-item">
					<div class="home-card-item-title">实时检测信息</div>
					<div class="home-monitor">
						<div class="flex-warp">
							<el-table :data="state.data" style="width: 100%">
								<el-table-column prop="username" label="用户名" align="center" />
								<el-table-column prop="weight" label="识别权重" align="center" />
								<el-table-column prop="conf" label="最小阈值" align="center" />
								<el-table-column prop="ai" label="AI助手" align="center" />
								<el-table-column prop="startTime" label="时间" align="center" />
							</el-table>
						</div>
					</div>
				</div>
			</el-col>
		</el-row>
		<el-row :gutter="15" class="home-card-three" style="margin-top: 15px;">
			<el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24">
				<div class="home-card-item">
					<div style="height: 100%" ref="homeLineRef"></div>
					<!-- <div style="height: 100%" ref="homeradarRef"></div> -->
				</div>
			</el-col>
		</el-row>
	</div>
</template>

<script setup lang="ts" name="home">
import { reactive, onMounted, ref, watch, nextTick, onActivated, markRaw } from 'vue';
import * as echarts from 'echarts';
import { storeToRefs } from 'pinia';
import { useThemeConfig } from '/@/stores/themeConfig';
import { useTagsViewRoutes } from '/@/stores/tagsViewRoutes';
import request from '/@/utils/request';

// 定义变量内容
const homeLineRef = ref();
const homePieRef = ref();
const homeBarRef = ref();
const homeradarRef = ref();
const storesTagsViewRoutes = useTagsViewRoutes();
const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);
const { isTagsViewCurrenFull } = storeToRefs(storesTagsViewRoutes);
const state = reactive({
	data: [] as any,
	global: {
		homeChartOne: null,
		homeChartTwo: null,
		homeCharThree: null,
		homeCharFour: null,
		dispose: [null, '', undefined],
	} as any,
	myCharts: [] as EmptyArrayType,
	charts: {
		theme: '',
		bgColor: '',
		color: '#303133',
	},
});

// 折线图
const initLineChart = () => {
	if (!state.global.dispose.some((b: any) => b === state.global.homeChartOne)) state.global.homeChartOne.dispose();
	state.global.homeChartOne = markRaw(echarts.init(homeLineRef.value, state.charts.theme));
	// 1. 统计每天的检测数量
	const counts: Record<string, number> = state.data.reduce((acc, prediction) => {
		// 提取日期部分，例如 "2025-02-11 13:01:33" 提取 "2025-02-11"
		const date = prediction.startTime.split(' ')[0];
		acc[date] = (acc[date] || 0) + 1;
		return acc;
	}, {} as Record<string, number>);

	// 2. 对所有日期按降序排序（最新日期在前）
	const sortedDatesDesc = Object.keys(counts).sort((a, b) => b.localeCompare(a));

	// 3. 取最新的前 10 天数据
	const latest7DatesDesc = sortedDatesDesc.slice(0, 10);

	// 4. 为了便于展示，将这 10 个日期按升序排序（即从最早到最新）
	const latest7Dates = latest7DatesDesc.sort((a, b) => a.localeCompare(b));

	// 5. 构造返回格式
	const result = {
		dateData: latest7Dates,              // 例如：["2025-02-05", "2025-02-06", ..., "2025-02-11"]
		valueData: latest7Dates.map(date => counts[date])
	};

	console.log(result);
	const option = {
		backgroundColor: state.charts.bgColor,
		title: {
			text: '近十日检测数量',
			x: 'left',
			textStyle: { fontSize: '15', color: state.charts.color },
		},
		grid: { top: 70, right: 20, bottom: 30, left: 30 },
		tooltip: { trigger: 'axis' },
		xAxis: {
			data: result.dateData,
		},
		yAxis: [
			{
				type: 'value',
				name: '检测数量',
				splitLine: { show: true, lineStyle: { type: 'dashed', color: '#f5f5f5' } },
			},
		],
		series: [
			{
				name: '数量',
				type: 'line',
				symbolSize: 6,
				symbol: 'circle',
				smooth: true,
				data: result.valueData,
				lineStyle: { color: '#9E87FF' },
				itemStyle: { color: '#9E87FF', borderColor: '#9E87FF' },
				areaStyle: {
					color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
						{ offset: 0, color: '#9E87FFb3' },
						{ offset: 1, color: '#9E87FF03' },
					]),
				},
				emphasis: {
					itemStyle: {
						color: {
							type: 'radial',
							x: 0.5,
							y: 0.5,
							r: 0.5,
							colorStops: [
								{ offset: 0, color: '#9E87FF' },
								{ offset: 0.4, color: '#9E87FF' },
								{ offset: 0.5, color: '#fff' },
								{ offset: 0.7, color: '#fff' },
								{ offset: 0.8, color: '#fff' },
								{ offset: 1, color: '#fff' },
							],
						},
						borderColor: '#9E87FF',
						borderWidth: 2,
					},
				},
			},
		],
	};
	state.global.homeChartOne.setOption(option);
	state.myCharts.push(state.global.homeChartOne);
};
// 饼图
const initPieChart = () => {
	if (!state.global.dispose.some((b: any) => b === state.global.homeChartTwo)) state.global.homeChartTwo.dispose();
	state.global.homeChartTwo = markRaw(echarts.init(homePieRef.value, state.charts.theme));
	// 1. 统计每个 username 的检测数量
	const usernameCounts = state.data.reduce((acc, prediction) => {
		const username = prediction.username;
		acc[username] = (acc[username] || 0) + 1;
		return acc;
	}, {});

	// 2. 将所有 username 按数量从大到小排序
	const sortedUsernames = Object.keys(usernameCounts).sort((a, b) => usernameCounts[b] - usernameCounts[a]);

	// 3. 只取数量最大的前 6 个数据
	const top5Usernames = sortedUsernames.slice(0, 6);
	const top5Values = top5Usernames.map(u => usernameCounts[u]);

	// 构造返回格式
	const result = {
		usernameData: top5Usernames, // 排序后的前五个用户名数组
		valueData: top5Values        // 对应的检测数量数组
	};

	// 将统计数据转换为饼图数据
	const pieData = result.usernameData.map((username, i) => ({
		name: username,
		value: result.valueData[i]
	}));

	// 配置颜色渐变列表和颜色线条数组
	const colorList = [
		{
			type: 'linear',
			x: 0,
			y: 0,
			x2: 1,
			y2: 1,
			colorStops: [
				{ offset: 0, color: 'rgba(51,192,205,0.01)' },
				{ offset: 1, color: 'rgba(51,192,205,0.57)' }
			],
			globalCoord: false
		},
		{
			type: 'linear',
			x: 1,
			y: 0,
			x2: 0,
			y2: 1,
			colorStops: [
				{ offset: 0, color: 'rgba(115,172,255,0.02)' },
				{ offset: 1, color: 'rgba(115,172,255,0.67)' }
			],
			globalCoord: false
		},
		{
			type: 'linear',
			x: 1,
			y: 0,
			x2: 0,
			y2: 0,
			colorStops: [
				{ offset: 0, color: 'rgba(158,135,255,0.02)' },
				{ offset: 1, color: 'rgba(158,135,255,0.57)' }
			],
			globalCoord: false
		},
		{
			type: 'linear',
			x: 0,
			y: 1,
			x2: 0,
			y2: 0,
			colorStops: [
				{ offset: 0, color: 'rgba(252,75,75,0.01)' },
				{ offset: 1, color: 'rgba(252,75,75,0.57)' }
			],
			globalCoord: false
		},
		{
			type: 'linear',
			x: 1,
			y: 1,
			x2: 1,
			y2: 0,
			colorStops: [
				{ offset: 0, color: 'rgba(253,138,106,0.01)' },
				{ offset: 1, color: '#FDB36ac2' }
			],
			globalCoord: false
		},
		{
			type: 'linear',
			x: 0,
			y: 0,
			x2: 1,
			y2: 0,
			colorStops: [
				{ offset: 0, color: 'rgba(254,206,67,0.12)' },
				{ offset: 1, color: '#FECE4391' }
			],
			globalCoord: false
		}
	];
	const colorLine = ['#33C0CD', '#73ACFF', '#9E87FF', '#FE6969', '#FDB36A', '#FECE43'];

	// 为饼图中的富文本标签生成样式
	function getRich() {
		let rich = {};
		colorLine.forEach((v, i) => {
			rich[`hr${i}`] = {
				backgroundColor: colorLine[i],
				borderRadius: 3,
				width: 3,
				height: 3,
				padding: [3, 3, 0, -12]
			};
			rich[`a${i}`] = {
				padding: [-11, 6, -20, 6],
				color: colorLine[i],
				backgroundColor: 'transparent',
				fontSize: 12
			};
		});
		return rich;
	}

	// 给每个饼图数据设置 labelLine 的颜色
	pieData.forEach((v: any, i) => {
		v.labelLine = {
			lineStyle: {
				width: 1,
				color: colorLine[i]
			}
		};
	});

	// 配置饼图的 option
	const option = {
		backgroundColor: state.charts.bgColor,
		title: {
			text: '不同用户的检测个数',
			x: 'left',
			textStyle: { fontSize: '15', color: state.charts.color },
		},
		legend: {
			top: 'bottom'
		},
		tooltip: {
			trigger: 'item'
		},
		series: [
			{
				type: 'pie',
				radius: '60%',         // 调整这里可以改变饼图的比例
				center: ['50%', '50%'],
				clockwise: true,
				avoidLabelOverlap: true,
				label: {
					show: true,
					position: 'outside',
					formatter: function (params) {
						const name = params.name;
						const percent = params.percent + '%';
						const index = params.dataIndex;
						return [`{a${index}|${name}：${percent}}`, `{hr${index}|}`].join('\n');
					},
					rich: getRich()
				},
				itemStyle: {
					normal: {
						color: function (params) {
							return colorList[params.dataIndex];
						}
					}
				},
				data: pieData,
				roseType: 'radius'
			}
		]
	};

	state.global.homeChartTwo.setOption(option);
	state.myCharts.push(state.global.homeChartTwo);
};
const initradarChart = () => {
	if (!state.global.dispose.some((b: any) => b === state.global.homeCharFour)) state.global.homeCharFour.dispose();
	state.global.homeCharFour = markRaw(echarts.init(homeradarRef.value, state.charts.theme));
	// 1. 按 username 分组，累计置信度的平均值和计数
	const confStatsByUser = state.data.reduce((acc, prediction) => {
		const { username, confidence } = prediction;
		const confidences = JSON.parse(confidence).map(percentStr => {
			const numValue = parseFloat(percentStr.replace('%', '')) / 100;
			return Number(numValue.toFixed(4));
		});
		const predictionAvg = confidences.reduce((sum, val) => sum + val, 0) / confidences.length;
		if (!acc[username]) {
			acc[username] = { total: predictionAvg, count: 1 };
		} else {
			acc[username].total += predictionAvg;
			acc[username].count += 1;
		}
		return acc;
	}, {});

	// 2. 计算每个用户的最终平均置信度（保持原始顺序）
	const avgConfData = Object.keys(confStatsByUser).map(username => ({
		username,
		avgConf: confStatsByUser[username].total / confStatsByUser[username].count,
	}));

	// 3. 取前7个用户（不排序）
	const top7AvgConfData = avgConfData.slice(0, 7);

	// 4. 格式化为百分比数值（保留两位小数）
	const result = {
		usernameData: top7AvgConfData.map(item => item.username),
		valueData: top7AvgConfData.map(item => Number((item.avgConf * 100).toFixed(2))),
	};

	// 构造雷达图所需数据
	const data = top7AvgConfData.map(item => Number((item.avgConf * 100).toFixed(2)));
	const indicatorNames = top7AvgConfData.map(item => item.username);
	const maxData = Array(data.length).fill(100);

	// 构造 indicator 数组
	const indicator = indicatorNames.map((name, idx) => ({ name, max: maxData[idx] }));

	// 辅助函数：生成内层数据
	const innerData = i => Array(data.length).fill(100 - 20 * i);

	// 构造系列数据
	const getData = data => {
		const series = [
			{
				type: 'radar',
				symbolSize: 10,
				symbol: 'circle',
				areaStyle: {
					color: 'rgba(108,80,243,0.5)',
					opacity: 0.3,
				},
				lineStyle: {
					color: new echarts.graphic.LinearGradient(
						0, 0, 0, 1,
						[
							{ offset: 0, color: 'rgba(108,80,243,0)' },
							{ offset: 1, color: 'rgba(108,80,243,0.3)' },
						],
						false
					),
					width: 3,
				},
				itemStyle: {
					color: '#fff',
					borderColor: new echarts.graphic.LinearGradient(
						0, 0, 0, 1,
						[
							{ offset: 0, color: 'rgba(108,80,243,0)' },
							{ offset: 1, color: 'rgba(108,80,243,0.3)' },
						],
						false
					),
					borderWidth: 4,
					opacity: 1,
				},
				label: { show: false },
				data: [{ value: data }],
				z: 100,
			},
		] as any;

		// 添加每个指标对应的内层系列
		data.forEach((_, i) => {
			series.push({
				type: 'radar',
				data: [{ value: innerData(i) }],
				symbol: 'none',
				lineStyle: { width: 0 },
				itemStyle: { color: '#fff' },
				areaStyle: {
					color: '#fff',
					shadowColor: 'rgba(14,122,191,0.15)',
					shadowBlur: 30,
					shadowOffsetY: 20,
				},
			});
		});
		return { series };
	};

	const optionData = getData(data);

	// 构造 ECharts 配置项
	const option = {
		backgroundColor: state.charts.bgColor,
		title: {
			text: '不同用户间的平均置信度',
			x: 'left',
			textStyle: { fontSize: '15', color: state.charts.color },
		},
		tooltip: {
			formatter: () =>
				indicatorNames
					.map((name, i) => `${name} : ${data[i]}%`)
					.join('<br>'),
		},
		radar: {
			// 设置半径为40%
			radius: '70%',
			center: ['50%', '50%'], // 也可以调整图表的位置
			indicator: indicator,
			splitArea: {
				show: true,
				areaStyle: {
					color: '#fff',
					shadowColor: 'rgba(108,80,243,0.3)', // 修正了此处颜色值
					shadowBlur: 30,
					shadowOffsetY: 20,
				},
			},
			splitLine: { show: false },
			axisLine: { show: false },
			axisLabel: { show: false },
			name: {
				textStyle: {
					rich: {
						a: {
							fontSize: '14',
							color: '#333',
							align: 'left',
							lineHeight: '20',
							fontWeight: 'bold',
						},
						b: {
							fontSize: '12',
							color: '#666',
							align: 'left',
						},
					},
				},
				formatter: params => {
					const idx = indicatorNames.indexOf(params);
					const percent = data[idx];
					return `{a|${percent}%}\n{b|${params}}`;
				},
			},
		},
		series: optionData.series,
	};

	state.global.homeCharFour.setOption(option);
	state.myCharts.push(state.global.homeCharFour);
};
// 柱状图
const initBarChart = () => {
	if (!state.global.dispose.some((b: any) => b === state.global.homeCharThree)) state.global.homeCharThree.dispose();
	state.global.homeCharThree = markRaw(echarts.init(homeBarRef.value, state.charts.theme));
	// 固定的六个类别
	const categories = ['举手', '读书', '写字', '玩手机', '低头', '趴在桌子上'];

	/**
	 * 统计数据中每个 label（已 JSON 字符串存储）中对应类别的出现次数
	 * @param data 数据数组
	 * @returns 一个元组，第一个数组为类别数组，第二个数组为对应的次数（字符串格式）
	 */
	function countLabelCategories(data: any[]): [string[], string[]] {
		// 初始化计数器
		const counts: Record<string, number> = {};
		categories.forEach(cat => {
			counts[cat] = 0;
		});

		data.forEach(item => {
			try {
				// 解析 label 字段（假设为 JSON 字符串格式，如 '["正常"]'）
				const labels: string[] = JSON.parse(item.label);
				labels.forEach(label => {
					if (categories.includes(label)) {
						counts[label]++;
					}
				});
			} catch (error) {
				console.error('解析 label 失败：', item, error);
			}
		});

		// 将计数转为字符串数组
		const countStrings = categories.map(cat => counts[cat].toString());
		return [categories, countStrings];
	}

	// 调用函数并输出结果
	const [catArr, countsArr] = countLabelCategories(state.data);
	const option = {
		backgroundColor: state.charts.bgColor,
		title: {
			text: '不同结果的检测个数',
			x: 'left',
			textStyle: { fontSize: '15', color: state.charts.color },
		},
		tooltip: { trigger: 'axis' },
		grid: { top: 70, right: 80, bottom: 30, left: 80 },
		xAxis: [
			{
				type: 'category',
				data: catArr,
				boundaryGap: true,
				axisTick: { show: false },
			},
		],
		yAxis: [
			{
				type: 'value',
				name: '个数',
				splitLine: { show: true, lineStyle: { type: 'dashed', color: '#f5f5f5' } },
			},
		],
		series: [
			{
				name: '平均值',
				type: 'bar',
				barWidth: 30,
				itemStyle: {
					color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
						{ offset: 0, color: 'rgba(108,80,243,0.3)' },
						{ offset: 1, color: 'rgba(108,80,243,0)' },
					]),
					//柱状图圆角
					borderRadius: [30, 30, 0, 0],
				},
				data: countsArr,
			},
		],
	};
	state.global.homeCharThree.setOption(option);
	state.myCharts.push(state.global.homeCharThree);
};
// 批量设置 echarts resize
const initEchartsResizeFun = () => {
	nextTick(() => {
		for (let i = 0; i < state.myCharts.length; i++) {
			setTimeout(() => {
				state.myCharts[i].resize();
			}, i * 1000);
		}
	});
};
// 批量设置 echarts resize
const initEchartsResize = () => {
	window.addEventListener('resize', initEchartsResizeFun);
};
// 页面加载时
onMounted(() => {
	request.get('/api/imgRecords/all').then((res) => {
		if (res.code == 0) {
			state.data = res.data.reverse();
		}
	});
	initEchartsResize();
});
// 由于页面缓存原因，keep-alive
onActivated(() => {
	initEchartsResizeFun();
});
// 监听 pinia 中的 tagsview 开启全屏变化，重新 resize 图表，防止不出现/大小不变等
watch(
	() => isTagsViewCurrenFull.value,
	() => {
		initEchartsResizeFun();
	}
);
// 监听 pinia 中是否开启深色主题
watch(
	() => themeConfig.value.isIsDark,
	(isIsDark) => {
		nextTick(() => {
			state.charts.theme = isIsDark ? 'dark' : '';
			state.charts.bgColor = isIsDark ? 'transparent' : '';
			state.charts.color = isIsDark ? '#dadada' : '#303133';
			setTimeout(() => {
				initLineChart();
				initradarChart();
				initPieChart();
				initBarChart();
			}, 500);
		});
	},
	{
		deep: true,
		immediate: true,
	}
);
</script>

<style scoped lang="scss">
$homeNavLengh: 8;

.home-container {
	overflow: hidden;

	.home-card-one,
	.home-card-two,
	.home-card-three {
		.home-card-item {
			width: 100%;
			height: 130px;
			border-radius: 4px;
			transition: all ease 0.3s;
			padding: 20px;
			overflow: hidden;
			background: var(--el-color-white);
			color: var(--el-text-color-primary);
			border: 1px solid var(--next-border-color-light);

			&:hover {
				box-shadow: 0 2px 12px var(--next-color-dark-hover);
				transition: all ease 0.3s;
			}

			&-icon {
				width: 70px;
				height: 70px;
				border-radius: 100%;
				flex-shrink: 1;

				i {
					color: var(--el-text-color-placeholder);
				}
			}

			&-title {
				font-size: 15px;
				font-weight: bold;
				height: 30px;
			}
		}
	}

	.home-card-one {
		@for $i from 0 through 3 {
			.home-one-animation#{$i} {
				opacity: 0;
				animation-name: error-num;
				animation-duration: 0.5s;
				animation-fill-mode: forwards;
				animation-delay: calc($i/4) + s;
			}
		}
	}

	.home-card-two,
	.home-card-three {
		.home-card-item {
			height: 400px;
			width: 100%;
			overflow: hidden;

			.home-monitor {
				height: 100%;

				.flex-warp-item {
					width: 25%;
					height: 111px;
					display: flex;

					.flex-warp-item-box {
						margin: auto;
						text-align: center;
						color: var(--el-text-color-primary);
						display: flex;
						border-radius: 5px;
						background: var(--next-bg-color);
						cursor: pointer;
						transition: all 0.3s ease;

						&:hover {
							background: var(--el-color-primary-light-9);
							transition: all 0.3s ease;
						}
					}

					@for $i from 0 through $homeNavLengh {
						.home-animation#{$i} {
							opacity: 0;
							animation-name: error-num;
							animation-duration: 0.5s;
							animation-fill-mode: forwards;
							animation-delay: calc($i/10) + s;
						}
					}
				}
			}
		}
	}
}
</style>
