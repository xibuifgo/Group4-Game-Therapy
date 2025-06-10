import Image from "next/image";
import styles from '../layout.module.scss';
import Bear from "../../../public/bear_db.png"
import Title from '../../../public/title.png';

const Navbar = () => (
    <div className={styles.Navbar}>
        <div className={styles.Top}>
            <Image 
            src={Bear}
            alt="Animated sleeping bear"
            />
            <Image 
            src={Title}
            alt="Balancimals written on a wooden board"
            />
        </div>
        <div className={styles.NavLinks}>
            <p>About Us</p>
            <p>Service</p>
            <p>Contact Us</p>
            <a href='\signup'>
                <div className={styles.SUButton}>
                    <p>Sign Up</p>
                </div>
            </a>
        </div>
    </div>
);

export default Navbar;