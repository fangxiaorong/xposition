package job.fscience.com.server;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import com.amap.api.location.AMapLocation;
import com.amap.api.location.AMapLocationClient;
import com.amap.api.location.AMapLocationClientOption;
import com.amap.api.location.AMapLocationListener;

public class PositionService extends Service implements AMapLocationListener {
    AMapLocationClient locationClient = null;

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();

        locationClient = new AMapLocationClient(getApplicationContext());
        locationClient.setLocationListener(this);

        AMapLocationClientOption option = new AMapLocationClientOption();
        option.setLocationMode(AMapLocationClientOption.AMapLocationMode.Hight_Accuracy);
        option.setOnceLocation(true);
        option.setOnceLocationLatest(true);
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        locationClient.startLocation();

        return super.onStartCommand(intent, flags, startId);
    }

    @Override
    public void onLocationChanged(AMapLocation aMapLocation) {
        if (aMapLocation != null && aMapLocation.getErrorCode() == 0) {
            System.out.println(aMapLocation.toStr());
        }
    }
}
