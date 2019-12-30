package job.fscience.com.xposition;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;

import job.fscience.com.xposition.service.ScreenManager;

public class SportsActivity extends AppCompatActivity {
//    // 动态注册锁屏等广播
//    private ScreenReceiverUtil mScreenListener;
//    // 1像素Activity管理类
//    private ScreenManager mScreenManager;
//    // 代码省略...
//
//    private ScreenReceiverUtil.SreenStateListener mScreenListenerer = new ScreenReceiverUtil.SreenStateListener() {
//        @Override
//        public void onSreenOn() {
//            // 移除"1像素"
//            mScreenManager.finishActivity();
//        }
//
//        @Override
//        public void onSreenOff() {
//            // 接到锁屏广播，将SportsActivity切换到可见模式
//            // "咕咚"、"乐动力"、"悦动圈"就是这么做滴
////            Intent intent = new Intent(SportsActivity.this,SportsActivity.class);
////            startActivity(intent);
//            // 如果你觉得，直接跳出SportActivity很不爽
//            // 那么，我们就制造个"1像素"惨案
//            mScreenManager.startActivity();
//        }
//
//        @Override
//        public void onUserPresent() {
//            // 解锁，暂不用，保留
//        }
//    };
//
//    @Override
//    protected void onCreate(Bundle savedInstanceState) {
//        super.onCreate(savedInstanceState);
//        setContentView(R.layout.activity_sports);
//        if(Contants.DEBUG)
//            Log.d(TAG,"--->onCreate");
//        // 1. 注册锁屏广播监听器
//        mScreenListener = new ScreenReceiverUtil(this);
//        mScreenManager = ScreenManager.getScreenManagerInstance(this);
//        mScreenListener.setScreenReceiverListener(mScreenListenerer);
//    }
//    // 代码省略...
}
