包含部分状态机以及移动铲子的接口
这次添加了边直走边转角度的接口，以及找球，找定位柱的代码
=======
<h2>篮球机器人比赛用状态机</h2>
<h1>队内人员请按规范书写此README！并且控制好分支和版本，确保无误后再上传master</h1>
<h1>其他人员请慎重使用！</h1>

<p>------------------------------------------------开发区--------------------------------------------------</p>

<p><font size="5px">robot_move_pkg</font></p>
<p>
    <ul>
    	<li>interpolation_function .......... 插值函数</li>
    	<ul>
    		<li>spline_config.py ............... 插值参数</li>
    		<li>growth_curve.py		............ 基于细菌生长曲线的速度插值 </li>
    		<li>growth_curve_demo.jpg .......... 插值效果图</li>
    	</ul>
        <li>config.py............设置一些参数的配置文件 </li>
        <li>move_a_distance.py...............移动一段指定距离 （进行速度插值平滑</li>
        <li>turn_an_angular.py................旋转一个指定的角度（进行速度插值平滑）</li>
        <li>linear_move.py....................边斜着走边转角度 (进行速度插值平滑)</li>
        <li>low_speed_linear_move ............以较低的速度进行斜着跑 (没有进行速度插值)</li>
        <li>move_in_robot  ...................在机器人坐标系下移动（进行速度插值平滑）</li>
        <li>move_to_home  ....................接受图像传来的信息，进行回家速度的发送</li>
        <li>go_along_circle ..................沿着圆弧跑</li>
      	
    </ul>
</p>
<p><font size="5px">robot_state_pkg</font></p>
<p>
    <ul>
        <li>get_robot_position.py..............获得机器人当前位置信息</li>
    </ul>
</p>
<p><font size="5px">ball_state_pkg</font></p>
<p>
    <ul>
        <li>find_oneball_state.py..............获得一个球当前位置信息</li>
        <li>find_twoball_state.py..............获得两个球当前位置以及色彩信息</li>
    </ul>
</p>
<p><font size="5px">cylinder_state_pkg</font></p>
<p>
    <ul>
        <li>find_cylinder_state.py..............获得定位柱的位置信息</li>
    </ul>
</p>
<p>strage_test.py...............一个状态机测试程序</p>
</br>
<p>-------------------------------------------------测试区-------------------------------------------------</p>
</br>
<p><font size="5px">2016-03测试情况</font></p>
    <p>测试人：liao-zhihan,hao</p>
<p>
    <ul>
        <li>move_a_distance.py:</li>
        <p>&nbsp;&nbsp;&nbsp;行走不太直，行走距离为给定距离的2倍左右</p>

        <li>turn_an_angular.py：</li>
        <p>&nbsp;&nbsp;&nbsp;在上位机停止发送数据后，机器人仍在旋转</p>

        <li>move_to_a_point.py:</li>
        <p>&nbsp;&nbsp;&nbsp;疑似代码有误，使斜跑时方向有问题</p>

        <li>get_robot_position.py：</li>
        <p>&nbsp;&nbsp;&nbsp;测试成功，无误</p>
    </ul>
</p>
<p><font size="5px">2016-7-15测试情况</font></p>
<p>
	<ul>
		<li>move_a_distance:</li>
		<p>&nbsp;&nbsp;&nbsp;比较准，但是会略歪一点</p>
		<li>turn_an_angular: </li>
		<p>&nbsp;&nbsp;&nbsp;修复了因tf产生的问题，遗留问题也基本解决，但是陀螺仪容易掉</p>
		<li>linear_move:</li>
		<p>&nbsp;&nbsp;&nbsp;斜着跑；斜着跑转角度。都基本没有问题了；但是参数可能需要调整一下</p>
		<li>get_robot_position:</li>
		<p>&nbsp;&nbsp;&nbsp;测试无误</p>
		<li>low_speed_linear_move:</li>
		<p>&nbsp;&nbsp;&nbsp;基本无误</p>
		<li>move_in_robot:</li>
		<p>&nbsp;&nbsp;&nbsp;尚未进行大量测试</p>
		<li>move_to_home:</li>
		<p>&nbsp;&nbsp;&nbsp;尚未测试</p>
		<li>go_along_circle:</li>
		<p>&nbsp;&nbsp;&nbsp;尚未进行大量测试</p>
	<ul>
</p>
