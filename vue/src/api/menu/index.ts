import request from '/@/utils/request';

/**
 * 菜单API接口
 * 
 * 系统菜单配置接口
 * @method getAdminMenu 获取管理员菜单
 * @method getTestMenu 获取普通用户菜单
 */
export function useMenuApi() {
	return {
		getAdminMenu: (params?: object) => {
			return request({
				url: '/api/menu/admin',
				method: 'get',
				params,
			});
		},
		getTestMenu: (params?: object) => {
			return request({
				url: '/api/menu/user',
				method: 'get',
				params,
			});
		},
	};
}
