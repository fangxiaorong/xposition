package job.fscience.com.xposition;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.Gravity;
import android.view.Window;
import android.view.WindowManager;

import job.fscience.com.xposition.service.ScreenManager;

public class SinglePixelActivity extends AppCompatActivity {
    private static final String TAG = "SinglePixelActivity";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // 获得activity的Window对象，设置其属性
        Window mWindow = getWindow();
        mWindow.setGravity(Gravity.LEFT | Gravity.TOP);
        WindowManager.LayoutParams attrParams = mWindow.getAttributes();
        attrParams.x = 0;
        attrParams.y = 0;
        attrParams.height = 1;
        attrParams.width = 1;
        mWindow.setAttributes(attrParams);
        // 绑定SinglePixelActivity到ScreenManager
        ScreenManager.getScreenManagerInstance(this).setSingleActivity(this);
    }

//    @Override
//    protected void onDestroy() {
//        if(! SystemUtils.isAppAlive(this, Contants.PACKAGE_NAME)){
//            Intent intentAlive = new Intent(this, SportsActivity.class);
//            intentAlive.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
//            startActivity(intentAlive);
//        }
//        super.onDestroy();
//    }
}
