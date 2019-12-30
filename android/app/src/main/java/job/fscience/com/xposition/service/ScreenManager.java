package job.fscience.com.xposition.service;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;

import java.lang.ref.WeakReference;

import job.fscience.com.xposition.SinglePixelActivity;

/**1像素管理类
  *
  * Created by jianddongguo on 2017/7/8.
  */
public class ScreenManager {
    private static final String TAG = "ScreenManager";
    private Context mContext;
    private static ScreenManager mSreenManager;
    // 使用弱引用，防止内存泄漏 
    private WeakReference<Activity> mActivityRef;

    private ScreenManager(Context mContext) {
        this.mContext = mContext;
    }

    // 单例模式
    public static ScreenManager getScreenManagerInstance(Context context) {
        if(mSreenManager == null) {
            mSreenManager = new ScreenManager(context);
        }
        return mSreenManager;
    }

    public void setSingleActivity(Activity mActivity) {
        mActivityRef = new WeakReference<>(mActivity);
    }

    public void startActivity(){
        Intent intent = new Intent(mContext, SinglePixelActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        mContext.startActivity(intent);
    }

    public void finishActivity(){
        if(mActivityRef != null){
            Activity mActivity = mActivityRef.get();
            if(mActivity != null){
                mActivity.finish();
            }
        }
    }
}
