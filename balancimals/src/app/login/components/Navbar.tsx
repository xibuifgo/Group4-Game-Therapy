import styles from '../layout.module.scss';

const Navbar = () => (
    <div className={styles.Navbar}>
        <p className={styles.NavLeft}>www.balancimals.com</p>
        <div className={styles.NavLinks}>
            <p>About Us</p>
            <p>Service</p>
            <p>Contact Us</p>
            <div className={styles.SUButton}>
            <p>Sign Up</p>
            </div>
        </div>
    </div>
);

export default Navbar;
