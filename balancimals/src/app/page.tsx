import Image from "next/image";
import styles from './home.module.scss';
import Bear from '../../public/bear.png';

export default function Home() {
  return (
    <div>
      <div className={styles.Banner}>
        <div className = {styles.Container}>
          <div className={styles.TitleDiv}>
            <h1 className={styles.Title}>BALANCIMALS</h1>
            <h3 className={styles.SubTitle}>Physiotherapy Made Fun!</h3>
          </div>
          <Image 
            src = {Bear}
            width = {300}
            height = {300}
            alt = "Pixel art of a sleeping bear"
          />
        </div>
      </div>
      <div className={styles.Body}>
        <div className={styles.ButtonContainer}>
          <div className={styles.ButtonDiv}>
            <h2 className={styles.Parent}>
              For Parents
            </h2>
            <a className={styles.BtnLink}>
              <div className = {styles.Btn}>
                <p>Download</p>
              </div>
            </a>
          </div>
          <div className={styles.ButtonDiv}>
            <h2 className={styles.Physio}>
              For Physiotherapists
            </h2>
            <a className={styles.BtnLink}>
              <div className = {styles.Btn}>
                <p>Log In</p>
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
