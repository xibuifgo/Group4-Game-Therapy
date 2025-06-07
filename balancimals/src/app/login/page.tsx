import Image from "next/image";
import styles from './Tlogin.module.scss';
import Prev from '../../../public/game_prev.png';
import Dude from '../../../public/physio_icon.png';
import Graph from '../../../public/stocks.png';
import Report from '../../../public/report.png';

export default function TLogIn() {
  return (
    <div>
        <div className={styles.LogIn}>
            <div className={styles.Inputs}>
                <h1>Balancimals</h1>
                <h3>Login to access physiotherapist portal</h3>
                <input type="text" id="username" placeholder="Enter Username" />
                <input type="password" id="password" placeholder="Enter Password" />
                <button className={styles.LIBtn}><p>Login</p></button>
            </div>
            <div className={styles.ImgBorder}>
                <Image 
                src = {Prev}
                width = {400}
                height = {400}
                layout = "responsive"
                alt = "Pixelated image of a bear sleeping in a forest"
                />
            </div>
        </div>
        <div className={styles.Bottom}>
            <h1>Our Services</h1>
            <div className={styles.Services}>
                <div className={styles.Card}>
                    <div className={styles.Icon}>
                        <Image 
                        src = {Dude}
                        width = {195}
                        height = {195}
                        layout = "responsive"
                        alt = "Icon of stickman walking with support"
                        />
                    </div>
                    <h4>Personalized Rehab Plans</h4>
                    <p>Customize and update rehab programs with therapist notes and adaptive difficulty settings.</p>
                </div>
                <div className={styles.Card}>
                    <div className={styles.Icon}>
                        <Image 
                        src = {Graph}
                        width = {195}
                        height = {195}
                        layout = "responsive"
                        alt = "Icon of stickman walking with support"
                        />
                    </div>
                    <h4>Progress Visualisation</h4>
                    <p>Charts, trend lines, and milestones make it easy to spot improvements or regression.</p>
                </div>
                <div className={styles.Card}>
                    <div className={styles.Icon}>
                        <Image 
                        src = {Report}
                        width = {195}
                        height = {195}
                        layout = "responsive"
                        alt = "Icon of stickman walking with support"
                        />
                    </div>
                    <h4>Automated Reporting</h4>
                    <p>Exportable summaries for insurance, referrals, or internal records.</p>
                </div>
            </div>
            <h1>Patient feedback</h1>
            <div className={styles.Reviews}>
                <div className={styles.Feedback}>
                    <div className={styles.Text}>
                        “I used to get bored with regular physio, but Balancimals makes it feel like a challenge I want to beat.”
                    </div>
                    <div className={styles.User}>
                        <div className={styles.UserImg}></div>
                        <div className={styles.UserInfo}>
                            <h5>Aisha, 10</h5>
                            <p>Patient diagnosed with Muscular Dystrophy</p>
                        </div>
                    </div>
                </div>
                <div className={styles.Feedback}>
                    <div className={styles.Text}>
                        “My daughter used to resist therapy, but she looks forward to the balance game every week. She's steadier and more confident now.”
                    </div>
                    <div className={styles.User}>
                        <div className={styles.UserImg}></div>
                        <div className={styles.UserInfo}>
                            <h5>Maya, Parent of 12 year old</h5>
                            <p>Daughter has Limb Girdle MD</p>
                        </div>
                    </div>
                </div>
                <div className={styles.Feedback}>
                    <div className={styles.Text}>
                        “Balancimals helped me track my progress in real-time. It’s encouraging to see small wins each session.”
                    </div>
                    <div className={styles.User}>
                        <div className={styles.UserImg}></div>
                        <div className={styles.UserInfo}>
                            <h5>Samuel, 8</h5>
                            <p>Patient diagnosed with Facioscapulohumeral MD</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
  );
}
