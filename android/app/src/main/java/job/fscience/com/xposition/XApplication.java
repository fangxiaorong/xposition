package job.fscience.com.xposition;

import android.app.AlarmManager;
import android.app.Application;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import job.fscience.com.server.PositionService;

public class XApplication extends Application {

    @Override
    public void onCreate() {
        super.onCreate();
        gpsAlarm();
    }

    public void gpsAlarm() {
        AlarmManager manager = (AlarmManager)getSystemService(Context.ALARM_SERVICE);
        Intent intent = new Intent(this, PositionService.class);
        PendingIntent pendingIntent = PendingIntent.getService(this, 0, intent, 0);
        manager.cancel(pendingIntent);
        manager.setRepeating(AlarmManager.RTC_WAKEUP, System.currentTimeMillis(), 3000, pendingIntent);

        System.out.println("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx");
    }
}
