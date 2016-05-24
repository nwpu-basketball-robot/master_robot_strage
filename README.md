<<<<<<< HEAD
包含部分状态机以及移动铲子的接口
=======
<h2>篮球机器人比赛用状态机</h2>
<h1>队内人员请按规范书写此README！并且控制好分支和版本，确保无误后再上传master</h1>
<h1>其他人员请慎重使用！</h1>

<p>------------------------------------------------开发区--------------------------------------------------</p>

<p><font size="5px">robot_move_pkg</font></p>
<p>
    <ul>
        <li>config.py............设置一些参数的配置文件</li>
        <li>move_a_distance.py...............移动一段指定距离</li>
        <li>turn_an_angular.py................旋转一个指定的角度</li>
        <li>move_to_a_point.py................移动到一个指定的点</li>
    </ul>
</p>
<p><font size="5px">robot_state_pkg</font></p>
<p>
    <ul>
        <li>get_robot_position.py..............获得机器人当前位置信息</li>
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
>>>>>>> d41aa20b485db43a3c212e87195b10342618c153
